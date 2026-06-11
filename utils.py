import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import cv2

GW, GH, POW = 160, 320, 2.5

# ── DEMOGRAFICI ────────────────────────────────────────────────
@st.cache_resource
def load_demographics(DEMO_C, DEMO_P):
    """ 
    Carica i dati demografici di due gruppi di soggetti da file CSV e restituisce un database indicizzato per ogni ID.
    """
    db = {}
    for path, group in [(DEMO_C, 'Control'), (DEMO_P, 'PD')]:
        try:
            # header=1 salta la riga 0 (categorie) e usa la riga 1 come intestazione
            df = pd.read_csv(path, header=1, dtype=str)
            if 'Age (years)' in df.columns and 'Age' not in df.columns:
                df = df.rename(columns={'Age (years)': 'Age'})
            for _, row in df.iterrows():     # row contiene una singola riga del DataFrame df sotto forma di oggetto pandas.Series --> rappresenta tutti i valori di una riga del CSV, con indice (nomi delle colonne) e valori (dati della riga)
                pid = str(row.iloc[0]).strip().lower()
                if pid and pid not in ('nan', '', 'subject id', '-'):
                    d = row.to_dict()    # trasforma una riga di un DataFrame pandas in un dizionario Python
                    d['_group'] = group
                    db[pid] = d
        except Exception as e:   
            st.warning(f"Demografici non caricati ({group}): {e}")    # salvo l’errore nella variabile e
    return db

def safe_value(demo_row, key, default='—'):
    """ 
    Recupera un valore dal dizionario contenente i dati demografici, gestendo valori mancanti o non validi. 
    """
    if not demo_row:
        return default
    v = str(demo_row.get(key, default)).strip()
    return v if v not in ('nan', 'None', '') else default

# ── IDS PER TASK ──────────────────────────────────────────────────────────────
@st.cache_data
def get_task_ids(fc, fp):
    """
    Estrae gli ID dei pazienti che hanno svolto i task a partire dai nomi delle colonne presenti in due file CSV.
    """
    ids = set()
    for path in [fc, fp]:
        try:
            df = pd.read_csv(path, low_memory=False, nrows=0)
            for c in df.columns:
                if '_' in c:
                    ids.add(c.split('_')[0].lower())
        except: pass    # se da errore continua
    ids.discard('time')    # non considero la colonna time
    return ids

# ── DATI PRESSIONI ────────────────────────────────────────────────────────────
@st.cache_data
def load_pressure(fc, fp, pid):
    """
    Carica i dati di pressione plantare di un paziente da uno dei due file CSV disponibili. 
    Cerca il paziente nei due file CSV, individua automaticamente il file corretto ed estrae i sensori di pressione del piede sinistro e destro.
    Inoltre calcola il Centro di Pressione (CoP) bilaterale dalla pedana e prepara i dati per la generazione
      delle heatmap plantari
    """
    pid = pid.strip().lower()
    # cerco il file che contiene le colonne del paziente
    df = None
    for path in [fc, fp]:
        try:
            tmp = pd.read_csv(path, low_memory=False)
            if any(col.startswith(pid + "_") for col in tmp.columns):
                df = tmp
                break
        except Exception:
            continue
    if df is None:
        return None, f"ID {pid.upper()} non trovato per questo task."

    # nomi delle colonne dei sensori di pressione
    left_cols = [f"{pid}_balance_LP{i}" for i in range(1, 17)]
    right_cols = [f"{pid}_balance_RP{i}" for i in range(1, 17)]
    # controllo che le colonne esistano
    if not all(col in df.columns for col in left_cols + right_cols):
        return None, f"Colonne di pressione non trovate per {pid.upper()}."

    # converto i dati in numeri
    lp = df[left_cols].apply(pd.to_numeric, errors="coerce")
    rp = df[right_cols].apply(pd.to_numeric, errors="coerce")
    # riempio eventuali valori mancanti con interpolazione lineare
    lp = lp.interpolate(method="linear", limit_direction="both").fillna(0)
    rp = rp.interpolate(method="linear", limit_direction="both").fillna(0)

    lp = lp.to_numpy()
    rp = rp.to_numpy()
    ts = df['Time_s'].values.astype(float)

   # ── CoP dalla pedana ──────────────────────────────────────────────────
    x_col = f"{pid}_balance_Walkway_X"
    y_col = f"{pid}_balance_Walkway_Y"
    p_col = f"{pid}_balance_WalkwayPressureLevel"
    cop_bx = []
    cop_by = []
    # ogni sensore della pedana misura 1.27 cm x 1.27 cm
    SENSOR_CM = 1.27
    if all(c in df.columns for c in [x_col, y_col, p_col]):
        for i in range(len(df)):
            try:
                # coordinate x e y dei sensori attivi al tempo i
                # i valori sono separati da "|"
                # moltiplico per 1.27 per passare da unità sensore a cm
                xs = [float(v) * SENSOR_CM for v in str(df[x_col].iloc[i]).split("|") if v not in ("nan", "")]
                ys = [float(v) * SENSOR_CM for v in str(df[y_col].iloc[i]).split("|") if v not in ("nan", "")]
                # livelli di pressione dei sensori attivi (da 0 a 15)
                # questi valori sono usati come pesi nel calcolo del CoP
                pressures = [float(v) for v in str(df[p_col].iloc[i]).split("|") if v not in ("nan", "")]
                n = min(len(xs), len(ys), len(pressures))
                xs = xs[:n]; ys = ys[:n]; pressures = pressures[:n]
                # calcolo del centro di pressione bilaterale: calcola la media delle coordinate x, ma dando più importanza ai sensori con pressione maggiore.
                if n > 0 and sum(pressures) > 0:
                    cop_x = np.average(xs, weights=pressures)
                    cop_y = np.average(ys, weights=pressures)
                else:
                    cop_x = np.nan
                    cop_y = np.nan
            except:
                # se in una riga ci sono valori non leggibili, salvo NaN invece di bloccare il programm
                cop_x = np.nan; cop_y = np.nan
            # salvo il CoP del frame corrente
            cop_bx.append(cop_x)
            cop_by.append(cop_y)
    else:
         # se mancano le colonne della pedana, creo vettori vuoti della stessa lunghezza del DataFrame
        cop_bx = [np.nan] * len(df)
        cop_by = [np.nan] * len(df)
    
    # interpolo eventuali valori mancanti del CoP
    cop_bx = pd.Series(cop_bx).interpolate(limit_direction='both').values
    cop_by = pd.Series(cop_by).interpolate(limit_direction='both').values
    # unisco tutte le pressioni dei due piedi e considero solo valori positivi
    pos_v = np.concatenate([lp.flatten(), rp.flatten()])
    pos_v = pos_v[pos_v > 0]
    # uso il 98° percentile come massimo della scala colori.
    # in questo modo eventuali picchi isolati non schiacciano tutta la heatmap verso colori troppo bassi
    vmax  = float(np.percentile(pos_v, 98)) if len(pos_v) else 1.0
    return dict(lp=lp, rp=rp, ts=ts, vmin=0.0, vmax=vmax, n_frames=len(ts), cop_bx=cop_bx, cop_by=cop_by), None

# ── MASCHERA ──────────────────────────────────────────────────────────────────
@st.cache_data
def extract_mask(path, gw=GW, gh=GH):
    """
    Estrae una maschera binaria del piede a partire da un'immagine.
    """
    img = cv2.imread(str(path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # segmentazione del piede --> prende il contorno scuro
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # trova i contorni
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # se non trova nulla
    if not contours:
        return np.zeros((gh, gw), dtype=bool)
    # prende il contorno più grande
    largest = max(contours, key=cv2.contourArea)

    # maschera binaria
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [largest], -1, 255, thickness=-1)
    # resize
    mask = Image.fromarray(mask).resize((gw, gh), Image.LANCZOS)
    return np.array(mask) > 128


# ── IDW ───────────────────────────────────────────────────────────────────────
@st.cache_data
def build_idw(sensors, gw, gh, power):
    """
    Calcola i pesi IDW (Inverse Distance Weighting) per ogni punto della griglia.
    Per ogni pixel dell'immagine, calcola quanto peso dare a ciascun sensore
    in base alla distanza: i sensori più vicini pesano di più.
    Serve a capire quanto ogni sensore deve influenzare ciascun punto della mappa plantare.
    """
    sensors = np.array(sensors)
    # creo una griglia di punti normalizzati tra 0 e 1
    # y_grid è invertito perché nell'immagine y=0 è in alto, ma y=0 è il tallone
    gx = np.linspace(0, 1, gw)
    gy = np.linspace(0, 1, gh)[::-1]
    GX, GY = np.meshgrid(gx, gy)
    # trasformo la griglia in una lista di punti (x, y)
    pts = np.stack([GX.ravel(), GY.ravel()], axis=1)
    # per ogni punto della griglia calcolo la differenza con tutti i sensori
    # pts ha forma (n_punti, 2), sensors ha forma (n_sensori, 2)
    # il risultato diff ha forma (n_punti, n_sensori, 2)
    diff = pts[:, None, :] - sensors[None, :, :]
    # calcolo la distanza al quadrato tra ogni punto e ogni sensore
    # clip evita divisione per zero se un punto coincide con un sensore
    d2 = np.clip((diff ** 2).sum(axis=2), 1e-10, None)
    # peso IDW: inversamente proporzionale alla distanza elevata a power
    # più power è alto, più i sensori lontani vengono ignorati
    w = 1.0 / d2 ** (power / 2)
    # normalizzo i pesi in modo che la somma per ogni punto sia 1
    w /= w.sum(axis=1, keepdims=True)
    return w

def heat_lut(n=256):
    """
    Crea una tabella di colori per rappresentare le pressioni con una scala tipo heatmap.
    La funzione crea una LUT, cioè una Look-Up Table.
    Ogni valore normalizzato tra 0 e 1 viene associato a un colore RGB.
    I valori bassi sono rappresentati con colori freddi, mentre i valori alti sono rappresentati con colori caldi.
    """
    # punti principali della scala colore
    stops=[(0,(8,0,120)),(0.12,(30,0,200)),(0.25,(0,80,255)),
           (0.40,(0,200,255)),(0.55,(0,255,180)),(0.68,(120,255,0)),
           (0.80,(255,220,0)),(0.90,(255,80,0)),(1.00,(220,0,0))]
    # array finale dei colori
    lut=np.zeros((n,3),np.uint8)
    for i in range(n):
        # valore normalizzato tra 0 e 1
        t=i/(n-1)
        # cerco tra quali due colori si trova t
        for j in range(len(stops)-1):
            t0,c0=stops[j]
            t1,c1=stops[j+1]
            if t0<=t<=t1:
                # percentuale di avanzamento tra i due colori
                f=(t-t0)/(t1-t0)
                # interpolazione RGB
                lut[i]=[int(c0[k]+f*(c1[k]-c0[k])) for k in range(3)]
                break
    return lut
LUT = heat_lut()

def render_single_frame(lp_frame, rp_frame, mask_L, mask_R, WL, WR, vmin, vmax):
    """
    Genera le mappe di pressione plantare per un singolo frame.
    Le immagini finali rappresentano la distribuzione delle pressioni plantari con una heatmap:
    - colori freddi (blu) -> pressione bassa
    - colori intermedi (verde/giallo) -> pressione media
    - colori caldi (rosso) -> pressione alta
    """
    images = []
    for pressure, mask, weights in [(lp_frame, mask_L, WL), (rp_frame, mask_R, WR)]:
        # interpolazione sulla griglia
        grid = (weights @ pressure).reshape(GH, GW)   # @ = moltiplicazione matriciale
        # normalizzazione tra 0 e 1
        norm = np.clip((grid - vmin) / (vmax - vmin + 1e-9), 0, 1)
        # conversione in colori
        idx = (norm * 255).astype(np.uint8)
        rgba = np.ones((GH, GW, 4), dtype=np.uint8) * 255
        rgba[:, :, :3] = LUT[idx]
        # sfondo trasparente fuori dal piede
        rgba[~mask, 3] = 0
        images.append(Image.fromarray(rgba, "RGBA"))
    return images[0], images[1]

def draw_sensors_on_image(img_pil, sensors):
    """
    Disegna i sensori numerati sopra l'immagine del piede.
    """
    draw = ImageDraw.Draw(img_pil)
    width, height = img_pil.size
    for k, (sx, sy) in enumerate(sensors):
        # coordinate del sensore nell'immagine
        px = int(sx * width)
        py = int((1 - sy) * height)
        r = 6
         # disegna il sensore
        draw.ellipse([px-r, py-r, px+r, py+r],
                     fill=(255, 255, 255, 160),
                     outline=(80, 80, 80, 128))
        # numero del sensore
        draw.text((px, py), str(k+1), fill=(26, 35, 64),
                  anchor="mm")
    return img_pil

# ── METRICHE COP ───────────────────────────────────────────────────────────────────────
def cop_metrics(cop_bx, cop_by):
    """
    Calcola alcune metriche posturali standard a partire dal Centro di Pressione (CoP) bilaterale.
    """
    # tengo solo i punti validi
    valid = ~np.isnan(cop_bx) & ~np.isnan(cop_by)
    x = cop_bx[valid]
    y = cop_by[valid]
    if len(x) < 2:
        return None

    sway_ml = float(np.std(x))
    sway_ap = float(np.std(y))

    # Sway path: somma delle distanze frame-by-frame
    dx = np.diff(x)
    dy = np.diff(y)
    sway_path = float(np.sum(np.sqrt(dx**2 + dy**2)))
    
    # calcolo la durata del task
    duration = (len(x) - 1) / 100.0
    if duration <= 0: return None
    # velocità media del CoP
    mean_vel = sway_path / duration

    # Area ellisse al 95% (metodo covarianza)
    # matrice di covarianza
    cov = np.cov(x, y)
    # autovalori della covarianza
    eigvals = np.linalg.eigvalsh(cov)
    # calcolo l'area dell'ellisse di confidenza al 95% tramite covarianza
    # gli autovalori della matrice di covarianza rappresentano la varianza lungo gli assi principali dell'ellissi
    # 5.991 è il valore critico del chi2 con 2 gradi di libertà al 95%
    area_95 = float(np.pi * 5.991 * np.sqrt(eigvals[0]) * np.sqrt(eigvals[1]))

    return dict(sway_ml=sway_ml, sway_ap=sway_ap, sway_path=sway_path, mean_vel=mean_vel, area_95=area_95)