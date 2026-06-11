import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import matplotlib.pyplot as plt
import matplotlib as mpl
from utils import (load_demographics, safe_value, get_task_ids, load_pressure, extract_mask, build_idw, render_single_frame, draw_sensors_on_image, cop_metrics, GW, GH, POW)

st.set_page_config(page_title="WearGait-PD · Balance - Single Patient Analysis", page_icon="icon.png", layout="wide")

IMG_L  = r"dataset\sole_left.png"
IMG_R  = r"dataset\sole_right.png"
DEMO_C = r"dataset\CONTROLS - Demographic+Clinical - datasetV1.csv"
DEMO_P = r"dataset\PD - Demographic+Clinical - datasetV1.csv"


TASK_LABELS = {
    "Task 1": "Stazione eretta — occhi aperti, piedi alla larghezza delle spalle",
    "Task 2": "Stazione eretta — occhi chiusi, piedi alla larghezza delle spalle",
    "Task 3": "Stazione eretta — occhi aperti, piedi uniti",
    "Task 4": "Stazione eretta — occhi chiusi, piedi uniti",
    "Task 5": "Stazione eretta — occhi aperti, tallone dx davanti a punta sx",
    "Task 6": "Stazione eretta — occhi aperti, tallone sx davanti a punta dx",
}
TASK_FILES = {t: (f"dataset\\Task_{i}C.csv", f"dataset\\Task_{i}PD.csv")      # prende tutti i task, genera automaticamente i path dei CSV e associa ogni task ai suoi file: control e pd
              for i, t in enumerate(TASK_LABELS, 1)}           


# ── IDW ───────────────────────────────────────────────────────────────────────
SENSORS_L = np.array([
    [0.6,0.11],[0.3,0.1],[0.6,0.26],[0.3,0.25],
    [0.6,0.41],[0.3,0.4],[0.74,0.59],[0.24,0.55],
    [0.85,0.73],[0.7,0.72],[0.55,0.71],[0.4,0.7],[0.25,0.69],
    [0.84,0.85],[0.60,0.84],[0.36,0.83],
])
SENSORS_R = np.column_stack([1.0 - SENSORS_L[:, 0], SENSORS_L[:, 1]])


# ── FUNZIONI SEMPLICI PER LA PARTE FINALE ────────────────────────────────────
@st.cache_data
def get_all_patient_ids():
    """ Legge gli ID paziente dai file dei task, usando solo l'header dei CSV, e restituisce la lista ordinata. """
    ids = set()      # non mantiene duplicati --> è utile per avere ID unici
    for fc, fp in TASK_FILES.values():     # in fc e fp si salva il path di ciascun task
        ids.update(get_task_ids(fc, fp))
    return sorted(ids)


def show_demographic_card(pid, demo_db):
    """Mostra i dati anagrafici principali di un paziente."""
    demo_row = demo_db.get(pid)
    group = demo_row.get("_group") if demo_row else None

    if group == "Control":
        badge = ":blue-badge[CONTROL]"
    elif group == "PD":
        badge = ":red-badge[PD]"
    else:
        badge = ""

    if not demo_row:
        st.warning("Dati demografici non disponibili per questo ID.")
        return

    age = safe_value(demo_row, 'Age')
    gender = {"Male": "M", "Female": "F"}.get(safe_value(demo_row, 'Gender'), "—")
    h_in = safe_value(demo_row, 'Height (in)')
    weight = safe_value(demo_row, 'Weight (kg)')

    try:
        h_str = f"{float(h_in)*2.54:.0f}"
    except:
        h_str = h_in

    # calcolo punteggio totale MDS-UPDRS parte III
    totale_updrs = 0
    has_updrs = False
    for colonna in demo_row:
        if colonna.startswith('MDSUPDRS_3-'):
            try:
                totale_updrs += int(float(demo_row[colonna]))
                has_updrs = True
            except:
                pass
    updrs3_str = str(totale_updrs) if has_updrs else '—'

    st.markdown(f"#### {pid.upper()} {badge}")
    with st.container(border=True, gap="xsmall"):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Età (anni)", f"{age}", border=True)
        col2.metric("Sesso", gender, border=True)
        col3.metric("Altezza (cm)", h_str, border=True)
        col4.metric("Peso (kg)", f"{weight}", border=True)
        col1, col2, col3,col4 = st.columns(4)
        col1.metric("MDS-UPDRS III", updrs3_str, border=True, help="La Parte III del MDS-UPDRS valuta la funzione motoria tramite esame clinico.\n\nÈ composta da 33 item, ciascuno con punteggio da 0 a 4, per un totale massimo di 132.  \nValuta: tremore a riposo, rigidità, bradicinesia, postura, andatura e stabilità posturale.\n\nPunteggi più alti indicano una maggiore compromissione motoria.")

        if group == 'PD':
            hy = safe_value(demo_row, 'Modified Hoehn & Yahr Score')
            try:
                hy_str = hy if float(hy) > 0 else '—'
            except:
                hy_str = '—'
            col2.metric("Anni dalla diagnosi", safe_value(demo_row, 'Years since PD diagnosis'), border=True)
            col3.metric("DBS", safe_value(demo_row, 'DBS?'), border=True, help="DBS significa Deep Brain Stimulation, cioè stimolazione cerebrale profonda.\n\nÈ un trattamento neurochirurgico usato per il Parkinson in cui vengono impiantati elettrodi in aree specifiche del cervello che inviano impulsi elettrici per ridurre i sintomi motori (tremore, rigidità, bradicinesia).  \nÈ rilevante clinicamente perché i pazienti con DBS attivo possono avere pattern di equilibrio e distribuzione delle pressioni plantari diversi rispetto ai PD senza DBS.\n\nNel dataset indica se il paziente con Parkinson ha questo trattamento.")
            col4.metric("H&Y Score", hy_str, border=True, help="La scala di Hoehn & Yahr classifica la progressione del Parkinson da 1 a 5:\n\n• 1 — sintomi solo su un lato del corpo, senza limitazioni funzionali  \n• 2 — sintomi bilaterali, senza problemi di equilibrio  \n• 3 — instabilità posturale lieve-moderata, ancora autonomo  \n• 4 — grave disabilità, ma ancora in grado di camminare  \n• 5 — in carrozzella o allettato senza assistenza\n\nValori intermedi (es. 1.5, 2.5) sono usati nella versione modificata.")


def show_pressure_metrics(data):
    """Calcola e visualizza alcune metriche riassuntive delle pressioni plantari."""
    lp, rp = data['lp'], data['rp']
    mean_l = float(np.mean(np.sum(lp, axis=1)))
    mean_r = float(np.mean(np.sum(rp, axis=1)))
    # retropiede: sensori 1-4 (indici 0-3)
    # avampiede: sensori 9-16 (indici 8-15)
    fore_l = float(np.mean(np.sum(lp[:, 8:], axis=1)))
    hind_l = float(np.mean(np.sum(lp[:, 0:4], axis=1)))
    fore_r = float(np.mean(np.sum(rp[:, 8:], axis=1)))
    hind_r = float(np.mean(np.sum(rp[:, 0:4], axis=1)))
    tot_fore = fore_l + fore_r
    tot_hind = hind_l + hind_r
    prop_fore = tot_fore / (tot_fore + tot_hind) if (tot_fore + tot_hind) > 0 else 0
    asymmetry = ((mean_r - mean_l) / (mean_r + mean_l)) * 100 if (mean_l + mean_r) > 0 else 0
    
    with st.container(border=True):
        col1, col2, col3= st.columns(3)
        col1.metric("Carico medio SX (N/cm²)", f"{mean_l:.2f}", border=True, help="Indice medio di carico pressorio del piede sinistro durante il task.\n\nÈ rilevante perché permette di capire se il paziente distribuisce il carico in modo simmetrico tra i due piedi — un carico medio molto diverso tra piede sinistro e destro indica uno sbilanciamento posturale, frequente nel Parkinson dove la rigidità e la bradicinesia tendono a essere asimmetriche.")
        col2.metric("Carico medio DX (N/cm²)", f"{mean_r:.2f}", border=True, help="Indice medio di carico pressorio del piede destro durante il task.\n\nÈ rilevante perché permette di capire se il paziente distribuisce il carico in modo simmetrico tra i due piedi — un carico medio molto diverso tra piede sinistro e destro indica uno sbilanciamento posturale, frequente nel Parkinson dove la rigidità e la bradicinesia tendono a essere asimmetriche.")
        col3.metric("Proporzione avampiede", f"{prop_fore:.1%}", border=True, help="Proporzione del carico plantare sull'avampiede (sensori 9–16) rispetto al carico plantare totale (avampiede + retropiede), calcolata su entrambi i piedi.\n\nUn valore superiore al 50% indica maggiore carico anteriore. Nel Parkinson la flessione del tronco in avanti tende ad aumentare questa proporzione.")        
        col1, col2, col3= st.columns(3)
        col1.metric("Asimmetria", f"{asymmetry:.1f}%", border=True, help="L'asimmetria descrive lo sbilanciamento medio tra piede destro e piede sinistro.\n\nIl valore è calcolato confrontando il carico totale del piede destro con quello del piede sinistro.\n\nUn valore vicino a 0 indica un carico abbastanza bilanciato.\nUn valore positivo indica maggiore carico a destra.\nUn valore negativo indica maggiore carico a sinistra.")


def make_colorbar_fig(vmin, vmax, width=70):
    """ Crea e visualizza una colorbar verticale per le mappe di pressione plantare. """

    # creo una figura matplotlib stretta e verticale
    fig, ax = plt.subplots(figsize=(0.35, 2.6), dpi=150)
    # creo la colorbar usando la scala "jet" e i valori minimo/massimo reali
    cb = fig.colorbar(mpl.cm.ScalarMappable( norm=mpl.colors.Normalize(vmin=vmin, vmax=vmax), cmap=mpl.colormaps["jet"]), cax=ax)
    # creo 5 valori da mostrare sulla barra: minimo, intermedi e massimo
    ticks = np.linspace(vmin, vmax, 5)
    # imposto i valori numerici da visualizzare accanto alla colorbar
    cb.set_ticks(ticks)
    cb.set_ticklabels([f"{t:.2f}" for t in ticks])
    # riduco la dimensione dei numeri e delle tacche
    cb.ax.tick_params(labelsize=6, length=2, pad=1)

    # salvo la figura in memoria come immagine png
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.02, transparent=True)
    # chiudo la figura per evitare accumulo di memoria
    plt.close(fig)
    # mostro la colorbar in Streamlit controllando la larghezza finale
    st.image(buf, width=width)


def show_feet_pair(img_L, img_R, width=220):
    with st.container(horizontal=True, horizontal_alignment="center", vertical_alignment="center", gap="xsmall"):
        st.image(img_L, width=width)
        st.image(img_R, width=width)


def show_pressure_graph(data, mask_L, mask_R, WL, WR):
    """ Visualizza le mappe di pressione plantare per un determinato frame temporale."""
    # selezione del tempo da visualizzare
    sec = st.slider("**Secondo**", 0.0, 10.0, 0.0, step=0.5, format="%.1f s")
    # conversione del tempo nell'indice del frame
    frame_idx = int(sec / 10 * (data['n_frames'] - 1))
    # generazione delle mappe di pressione
    img_L, img_R = render_single_frame(data['lp'][frame_idx], data['rp'][frame_idx], mask_L, mask_R, WL, WR, data['vmin'], data['vmax'])
    # aggiunta dei sensori numerati
    img_L = draw_sensors_on_image(img_L.copy(), SENSORS_L.tolist())
    img_R = draw_sensors_on_image(img_R.copy(), SENSORS_R.tolist())

    # visualizzazione immagini e metriche
    with st.container(horizontal=True, horizontal_alignment="center", vertical_alignment="center", gap="xxsmall"):
        show_feet_pair(img_L, img_R)
        make_colorbar_fig(0, data["vmax"])
    st.caption("La scala colori delle sagome è normalizzata al 98° percentile delle pressioni, per evitare che picchi isolati riducano la leggibilità della mappa.", text_alignment="center")
    st.write("")
    st.markdown("#### Sintesi pressioni")
    show_pressure_metrics(data)


def show_patient_feet(pid, task, img_L, img_R):
    with st.container(horizontal_alignment="center", gap="xsmall"):
        st.markdown(f"##### **{pid.upper()} — {task}**", text_alignment="center")
        show_feet_pair(img_L, img_R)


def show_compare_graph(pid1, task1, data1, pid2, task2, data2, mask_L, mask_R, WL, WR):
    """ Visualizza il confronto tra due pazienti nelle mappe di pressione plantare. """
    n = min(data1['n_frames'], data2['n_frames'])
    sec = st.slider("**Secondo**", 0.0, 10.0, 0.0, step=0.5, format="%.1f s")
    frame_idx = int(sec / 10 * (n - 1))
    common_vmax = max(data1["vmax"], data2["vmax"])
    
    img1_L, img1_R = render_single_frame(data1['lp'][frame_idx], data1['rp'][frame_idx], mask_L, mask_R, WL, WR, data1['vmin'], common_vmax)
    img1_L = draw_sensors_on_image(img1_L.copy(), SENSORS_L.tolist())
    img1_R = draw_sensors_on_image(img1_R.copy(), SENSORS_R.tolist())

    img2_L, img2_R = render_single_frame(data2['lp'][frame_idx], data2['rp'][frame_idx], mask_L, mask_R, WL, WR, data2['vmin'], common_vmax)
    img2_L = draw_sensors_on_image(img2_L.copy(), SENSORS_L.tolist())
    img2_R = draw_sensors_on_image(img2_R.copy(), SENSORS_R.tolist())

    with st.container(horizontal=True, horizontal_alignment="center", vertical_alignment="center", gap="medium"):
        show_patient_feet(pid1, task1, img1_L, img1_R)
        make_colorbar_fig(0, common_vmax)
        show_patient_feet(pid2, task2, img2_L, img2_R)
    st.caption("La scala colori delle sagome è normalizzata al 98° percentile delle pressioni, per evitare che picchi isolati riducano la leggibilità della mappa.", text_alignment="center")
    st.write("")
    st.markdown("#### Sintesi pressioni")
    mcol1, mcol2 = st.columns(2)
    with mcol1:
        st.markdown(f"##### **{pid1.upper()}**")
        show_pressure_metrics(data1)
    with mcol2:
        st.markdown(f"##### **{pid2.upper()}**")
        show_pressure_metrics(data2)


def render_cop_metrics(m, pid=None):
    """Mostra le metriche CoP di un singolo paziente."""
    if m is None:
        st.warning("Metriche CoP non disponibili.")
        return
    if pid is not None:
        st.markdown(f"###### **{pid.upper()}**")
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Sway ML (cm)", f"{m['sway_ml']:.2f}", border=True, help="Deviazione standard della posizione del CoP in direzione medio-laterale.\n\nValori elevati indicano una maggiore variabilità dell'oscillazione destra-sinistra, associata a ridotta stabilità posturale.\n\nNel Parkinson è spesso aumentata a causa del deficit di controllo posturale.")
        col2.metric("Sway AP (cm)", f"{m['sway_ap']:.2f}", border=True, help="Deviazione standard della posizione del CoP in direzione antero-posteriore.\n\nValori elevati indicano una maggiore variabilità dell'oscillazione avanti-indietro, associata a ridotta stabilità posturale.\n\nÈ la componente dello sway più influenzata dalla visione: nei task a occhi chiusi tende ad aumentare perché il sistema visivo non può più contribuire al controllo dell'equilibrio.")
        col3.metric("Sway path (cm)", f"{m['sway_path']:.2f}", border=True, help="Lunghezza totale del percorso del CoP nei 10 secondi.  \nValori elevati indicano maggiore instabilità posturale.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Velocità media (cm/s)", f"{m['mean_vel']:.2f}", border=True, help="Sway path diviso la durata del task (10 s).  \nÈ la metrica più usata in letteratura per quantificare lo sway.")
        col2.metric("Area ellisse 95% (cm²)", f"{m['area_95']:.2f}", border=True, help="Area dell'ellisse di confidenza al 95% della distribuzione spaziale del CoP.  \nUn'area più grande indica una maggiore dispersione del CoP e quindi minore stabilità posturale.")


def show_cop_metrics(data1, pid1, data2=None, pid2=None):
    """ Calcola e visualizza le metriche posturali del centro di pressione. """
    m1 = cop_metrics(data1['cop_bx'], data1['cop_by'])
    if data2 is None:
        render_cop_metrics(m1)
    else:
        m2 = cop_metrics(data2['cop_bx'], data2['cop_by'])
        col1, col2 = st.columns(2)
        with col1:
            render_cop_metrics(m1, pid1)
        with col2:
            render_cop_metrics(m2, pid2)


def show_cop_section(data1, pid1, data2=None, pid2=None):
    """ Visualizza la distribuzione spaziale del Centro di Pressione (CoP) e le relative metriche posturali. """
    st.divider()
    st.subheader("**Centro di Pressione — Distribuzione spaziale**")

    def make_fig(data, pid):
        """ Crea il grafico di densità del CoP per un paziente. """
        # creo un DataFrame con le coordinate del CoP
        cop_x_centered = data['cop_bx'] - np.nanmean(data['cop_bx'])
        cop_y_centered = data['cop_by'] - np.nanmean(data['cop_by'])
        df_cop = pd.DataFrame({'cop_x': cop_x_centered, 'cop_y': cop_y_centered}).dropna()

        # grafico della distribuzione spaziale del CoP
        fig = px.density_contour(df_cop, x='cop_x', y='cop_y', title=f'{pid.upper()} — CoP bilaterale')
         # coloro le aree di densità
        fig.update_traces(contours_coloring='fill', colorscale='Blues')
        fig.update_layout(height=400, xaxis_title='Spostamento ML (cm)', yaxis_title='Spostamento AP (cm)', paper_bgcolor='white', plot_bgcolor='white')
        return fig

    if data2 is None:
        _, center, _ = st.columns([0.08, 0.84, 0.08])
        with center:
            st.plotly_chart(make_fig(data1, pid1), use_container_width=True)
            st.caption("Distribuzione spaziale del CoP bilaterale durante i 10 secondi. Le zone più dense indicano dove il CoP ha trascorso più tempo. Un'area ampia indica maggiore oscillazione posturale (sway).", text_alignment="center")
            st.write("")
            st.markdown("#### Metriche posturali — Centro di Pressione")
            show_cop_metrics(data1, pid1)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(make_fig(data1, pid1), use_container_width=True)
        with col2:
            st.plotly_chart(make_fig(data2, pid2), use_container_width=True)
        st.caption(body = "Distribuzione spaziale del CoP bilaterale durante i 10 secondi. Le zone più dense indicano dove il CoP ha trascorso più tempo. Un'area ampia indica maggiore oscillazione posturale (sway).", text_alignment="center")
        st.markdown("#### Metriche posturali — Centro di Pressione")
        show_cop_metrics(data1, pid1, data2, pid2)


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
st.title("Balance - Single Patient Analysis")
st.caption("I partecipanti sono stati sottoposti a 6 sottocompiti di equilibrio statico in stazione eretta, registrati tramite solette sensorizzate (Moticon OpenGo) e una pedana baropodometrica (ProtoKinetics Zeno Walkway). Per ciascun sottocompito, il partecipante saliva sulla pedana, manteneva la posizione richiesta per 10 secondi, quindi scendeva — permettendo così di segmentare automaticamente i dati per sottocompito. \n\nI task variano per condizione visiva (occhi aperti o chiusi) e posizione dei piedi (larghezza delle spalle, piedi uniti, posizione tandem), consentendo di valutare il contributo del sistema visivo e la capacità di mantenere l'equilibrio in condizioni di crescente difficoltà.", text_alignment="justify" )
st.markdown("<hr style='border-top:3px solid orange;margin-top:-5px;'>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    gruppo_filtro_1 = st.radio("Gruppo paziente 1", options=["Tutti", "Control", "PD"], key="gruppo_filtro_1")

    demo_db = load_demographics(DEMO_C, DEMO_P)
    all_patients = get_all_patient_ids()

    if gruppo_filtro_1 == "Tutti":
        pazienti_filtrati_1 = all_patients
    else:
        pazienti_filtrati_1 = [
            p for p in all_patients
            if demo_db.get(p, {}).get("_group") == gruppo_filtro_1
        ]

    if len(pazienti_filtrati_1) == 0:
        st.warning("Nessun paziente trovato per questo gruppo.")
        st.stop()

    default_patient_1 = st.session_state.get("selected_patient", None)
    if default_patient_1 is not None:
        default_patient_1 = default_patient_1.strip().lower()

    default_index_1 = (pazienti_filtrati_1.index(default_patient_1) if default_patient_1 in pazienti_filtrati_1 else 0)

    patient_id_1 = st.selectbox("ID paziente 1", options=pazienti_filtrati_1, index=default_index_1, format_func=lambda x: x.upper(), key="patient_id_1")
    task_sel_1 = st.selectbox("Task paziente 1", options=list(TASK_LABELS.keys()), format_func=lambda t: f"{t}  —  {TASK_LABELS[t]}", key="task_sel_1")

    st.divider()

    comparison_type = st.pills("Aggiungi confronto", options=["Stesso paziente, task diverso", "Paziente diverso"], selection_mode="single", key="comparison_type")
    if comparison_type == "Stesso paziente, task diverso":
        altri_task = [t for t in TASK_LABELS.keys() if t != task_sel_1]
        task_sel_2 = st.selectbox("Task da confrontare", options=altri_task, format_func=lambda t: f"{t}  —  {TASK_LABELS[t]}", key="task_sel_2")
        patient_id_2 = patient_id_1

    elif comparison_type == "Paziente diverso":
        gruppo_filtro_2 = st.radio("Gruppo paziente 2", options=["Tutti", "Control", "PD"], key="gruppo_filtro_2")
        if gruppo_filtro_2 == "Tutti":
            pazienti_filtrati_2 = [p for p in all_patients if p != patient_id_1]
        else:
            pazienti_filtrati_2 = [
                p for p in all_patients
                if demo_db.get(p, {}).get("_group") == gruppo_filtro_2 and p != patient_id_1
            ]
        patient_id_2 = st.selectbox("ID paziente 2", options=pazienti_filtrati_2, format_func=lambda x: x.upper(), key="patient_id_2")
        task_sel_2 = st.selectbox("Task paziente 2", options=list(TASK_LABELS.keys()), format_func=lambda t: f"{t}  —  {TASK_LABELS[t]}", key="task_sel_2")
    else:
        patient_id_2 = None
        task_sel_2 = None

pid1 = patient_id_1.strip().lower()
pid2 = patient_id_2.strip().lower() if patient_id_2 is not None else None

# ── Demografici ───────────────────────────────────────────────────────────────
st.subheader("**Dati Demografici**")
if pid2 is None:
    show_demographic_card(pid1, demo_db)
else:
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        show_demographic_card(pid1, demo_db)
    with dcol2:
        show_demographic_card(pid2, demo_db)

# ── Caricamento dati pressioni ────────────────────────────────────────────────
fc1, fp1 = TASK_FILES[task_sel_1]
data1, err1 = load_pressure(fc1, fp1, pid1)
if err1:
    st.warning(err1)
    st.stop()

data2, err2 = None, None
if pid2 is not None:
    fc2, fp2 = TASK_FILES[task_sel_2]
    data2, err2 = load_pressure(fc2, fp2, pid2)
    if err2:
        st.warning(err2)
        st.stop()

# ── Maschere e IDW ────────────────────────────────────────────────────────────
try:
    mask_L = extract_mask(IMG_L)
    mask_R = extract_mask(IMG_R)
except Exception as e:
    st.error(f"Immagini sagoma non trovate nella cartella dataset: {e}")
    st.stop()

WL = build_idw(SENSORS_L, GW, GH, POW)    # matrice con i pesi normalizzati
WR = build_idw(SENSORS_R, GW, GH, POW)

# ── Grafici ───────────────────────────────────────────────────────────────────
st.divider()
st.subheader("**Distribuzione delle pressioni plantari**")

if pid2 is None:
    _, center, _ = st.columns([0.08, 0.84, 0.08])
    with center:
        show_pressure_graph(data1, mask_L, mask_R, WL, WR)
else:
    show_compare_graph(pid1, task_sel_1, data1, pid2, task_sel_2, data2, mask_L, mask_R, WL, WR)
    
show_cop_section(data1, pid1, data2, pid2)