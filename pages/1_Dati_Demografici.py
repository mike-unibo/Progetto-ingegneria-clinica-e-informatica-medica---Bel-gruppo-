import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from test_statistici import esegui_test

#  Configurazione della pagina: imposto titolo, icona e stato iniziale della sidebar
st.set_page_config(page_title="WearGait-PD · Dati Demografici", page_icon="icon.png", layout="wide")

# Colori usati nei grafici
PD_COL   = "crimson"
CTRL_COL = "royalblue"
MALE_COL = "#728FFA"
FEM_COL  = "#FA729F"
MOCA_COL = "royalblue"

# Dizionario indici UPDRS — chiave = nome colonna nel CSV, valore = nome leggibile
INDICI = {
    "UPDRS_III":         "UPDRS III — Punteggio Totale (0-132)",
    "MDSUPDRS_3-9":      "3-9  · Alzarsi dalla sedia",
    "MDSUPDRS_3-10":     "3-10 · Andatura",
    "MDSUPDRS_3-11":     "3-11 · Freezing dell'andatura",
    "MDSUPDRS_3-12":     "3-12 · Stabilità posturale",
    "MDSUPDRS_3-14":     "3-14 · Bradicinesia globale",
    "MDSUPDRS_3-17-RUE": "3-17 · Tremore a riposo — Arto Sup. Destro",
    "MDSUPDRS_3-17-LUE": "3-17 · Tremore a riposo — Arto Sup. Sinistro",
    "MDSUPDRS_3-17-RLE": "3-17 · Tremore a riposo — Arto Inf. Destro",
    "MDSUPDRS_3-17-LLE": "3-17 · Tremore a riposo — Arto Inf. Sinistro",
}

# Dizionario per la visualizzazione degli help descrittivi degli item UPDRS III
HELP_INDICI = {
    "UPDRS_III":         "Somma dei 33 sotto-item della parte motoria dell'MDS-UPDRS. Valori più alti indicano maggiore compromissione motoria. Range: 0-132.",
    "MDSUPDRS_3-9":      "Valuta la capacità di alzarsi da una sedia senza usare le braccia. Score 0 = normale, 4 = incapace senza aiuto.",
    "MDSUPDRS_3-10":     "Osservazione dell'andatura su una distanza standard. Valuta velocità, lunghezza del passo, freezing e uso di ausili.",
    "MDSUPDRS_3-11":     "Presenza di blocchi motori (freezing) durante il cammino, le svolte o l'inizio del movimento. Score 0 = assente, 4 = frequente e causa cadute.",
    "MDSUPDRS_3-12":     "Test del pull: il clinico tira il paziente per le spalle e osserva la risposta posturale. Score 0 = normale, 4 = cade senza tentativo di recupero.",
    "MDSUPDRS_3-14":     "Impressione globale del clinico sulla lentezza dei movimenti durante tutta la valutazione. Considera ampiezza e velocità.",
    "MDSUPDRS_3-17-RUE": "Tremore a riposo all'arto superiore destro. Valutato con l'arto appoggiato e il paziente distratto. Score 0 = assente, 4 = ampiezza > 10 cm.",
    "MDSUPDRS_3-17-LUE": "Tremore a riposo all'arto superiore sinistro. Stessa scala del lato destro.",
    "MDSUPDRS_3-17-RLE": "Tremore a riposo all'arto inferiore destro (gamba/piede). Score 0 = assente, 4 = ampiezza > 10 cm.",
    "MDSUPDRS_3-17-LLE": "Tremore a riposo all'arto inferiore sinistro. Stessa scala del lato destro.",
}

# Lista completa dei 33 sotto-item UPDRS III — usata per calcolare il punteggio totale
colonne_updrs = [
    "MDSUPDRS_3-1",      "MDSUPDRS_3-2",      "MDSUPDRS_3-3-Neck", "MDSUPDRS_3-3-RUE",  "MDSUPDRS_3-3-LUE",
    "MDSUPDRS_3-3-RLE",  "MDSUPDRS_3-3-LLE",  "MDSUPDRS_3-4-R",    "MDSUPDRS_3-4-L",    "MDSUPDRS_3-5-R",
    "MDSUPDRS_3-5-L",    "MDSUPDRS_3-6-R",    "MDSUPDRS_3-6-L",    "MDSUPDRS_3-7-R",    "MDSUPDRS_3-7-L",
    "MDSUPDRS_3-8-R",    "MDSUPDRS_3-8-L",    "MDSUPDRS_3-9",      "MDSUPDRS_3-10",     "MDSUPDRS_3-11",
    "MDSUPDRS_3-12",     "MDSUPDRS_3-13",     "MDSUPDRS_3-14",     "MDSUPDRS_3-15-R",   "MDSUPDRS_3-15-L",
    "MDSUPDRS_3-16-R",   "MDSUPDRS_3-16-L",   "MDSUPDRS_3-17-RUE", "MDSUPDRS_3-17-LUE", "MDSUPDRS_3-17-RLE",
    "MDSUPDRS_3-17-LLE", "MDSUPDRS_3-17-LipJaw", "MDSUPDRS_3-18",
]

#  Caricamento dei dati dai file CSV

# Memorizza in cache il DataFrame caricato: evita di rileggere e rielaborare i CSV ad ogni reset dello script
@st.cache_data(show_spinner=False)

def load():
    # Carica i due CSV (header=1 per saltare la prima riga di intestazione del dataset) e uniforma il nome della colonna età
    pd_df   = pd.read_csv("dataset/PD - Demographic+Clinical - datasetV1.csv", header=1)
    ctrl_df = pd.read_csv("dataset/CONTROLS - Demographic+Clinical - datasetV1.csv", header=1)
    pd_df.rename(columns={"Age (years)": "Age"}, inplace=True)

    # Converte i 33 sotto-item UPDRS III in numerico  Converte i 33 sotto-item UPDRS III in numerico ("-" diventa NaN) 
    # e ricostruisce il punteggio totale (richiede almeno metà item compilati)
    for colonna in colonne_updrs:
        pd_df[colonna]   = pd.to_numeric(pd_df[colonna],   errors="coerce")
        ctrl_df[colonna] = pd.to_numeric(ctrl_df[colonna], errors="coerce")
    pd_df["UPDRS_III"]   = pd_df[colonne_updrs].sum(axis=1, min_count=len(colonne_updrs)//2)
    ctrl_df["UPDRS_III"] = ctrl_df[colonne_updrs].sum(axis=1, min_count=len(colonne_updrs)//2)

    # Etichetta il gruppo di appartenenza, poi normalizza età (numerico) e sesso ("-" → NaN) per entrambi i dataset
    pd_df["group"]   = "PD"
    pd_df["group"]   = "PD"
    ctrl_df["group"] = "Controllo"
    for gruppo_df in [pd_df, ctrl_df]:
        gruppo_df["Age"] = pd.to_numeric(gruppo_df["Age"], errors="coerce")
        gruppo_df["Sex"] = gruppo_df["Sex"].replace("-", np.nan)

    # Unisce PD e controlli in un unico DataFrame con indice ricalcolato
    return pd.concat([pd_df, ctrl_df], ignore_index=True)

# Richiamo la funzione di caricamento dei dati e creo i due data frame
df      = load()
df_pd   = df[df["group"] == "PD"]
df_ctrl = df[df["group"] == "Controllo"]

# Statistiche di base
N_PD   = len(df_pd)
N_CTRL = len(df_ctrl)
N_TOT  = N_PD + N_CTRL
age_pd   = df_pd["Age"].mean()
age_ctrl = df_ctrl["Age"].mean()

# Definisco la funzione che utilizzo per la visualizzazione della distribuzione del sesso
def sex_counts(sub):
    vc = sub["Sex"].value_counts()
    return int(vc.get("Male", 0)), int(vc.get("Female", 0))

m_pd, f_pd     = sex_counts(df_pd)
m_ctrl, f_ctrl = sex_counts(df_ctrl)
m_tot          = m_pd + m_ctrl
f_tot          = f_pd + f_ctrl

# Creo una sidebar per i filtri interattivi
with st.sidebar:
    st.markdown("### MoCA Score")
    range_options = {
        "Tutti (0-30)":    (0,  30),
        "Normale (26-30)": (26, 30),
        "MCI (18-25)":     (18, 25),
        "Deterioro (≤17)": (0,  17),
    }
    range_sel = st.selectbox("Intervallo MoCA", options=list(range_options.keys()))

    st.markdown("---")
    st.markdown("### Indici UPDRS III")

    # Selettore dell'indice UPDRS III: il menù salva il nome-colonna del CSV, ma format_func mostra all'utente l'etichetta leggibile
    indice_sel = st.selectbox(
        "Seleziona l'indice da visualizzare",
        options=list(INDICI.keys()),
        format_func=lambda x: INDICI[x],
    )
    gruppo_sel = st.radio(
        "Gruppo",
        options=["Entrambi", "Solo PD", "Solo Controlli"],
        horizontal=False,
        key="radio_gruppo",
    )

#  Intestazione della pagina
st.title("Dati Demografici", text_alignment="center")
st.markdown(
    "Panoramica clinica e demografica dei 185 partecipanti dello studio. "
    "Esplora la composizione del campione, la funzione cognitiva e gli indici di gravità motoria, "
    "con confronti statistici tra pazienti PD e controlli sani."
)
st.markdown("<hr style='border-top: 3px solid blue; margin-top: -5px;'>", unsafe_allow_html=True)

#  Creazione delle KPI riassuntive
st.subheader("Riepilogo del Campione")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Partecipanti totali",      N_TOT,             border=True)
c2.metric("Pazienti PD",              N_PD,              border=True)
c3.metric("Controlli",                N_CTRL,            border=True)
c4.metric("Età media PD (aa)",        f"{age_pd:.0f}",   border=True)
c5.metric("Età media Controlli (aa)", f"{age_ctrl:.0f}", border=True)
st.divider()

#  SEZIONE 1: Distribuzione del Campione
st.markdown("##### Distribuzione del Campione")
g1, g2 = st.columns([2, 1]) # disposizione su due colonne per avere i grafici affiancati

with g2:
    df_sesso = pd.DataFrame({
        "Sesso":  ["Maschi", "Femmine"],
        "Numero": [m_tot,    f_tot],
    })
    fig = px.pie(
        df_sesso, names="Sesso", values="Numero", hole=0.4, color="Sesso",
        color_discrete_map={"Maschi": MALE_COL, "Femmine": FEM_COL},
        title="Sesso (totale)",
    )
    fig.update_traces(textinfo="label+percent", textfont_size=15)
    st.plotly_chart(fig, width="stretch")

# Creazione dei "bottoni" per il fitlraggio della visualizzazione
gruppo_eta = st.radio(
    "Mostra", options=["Entrambi", "Solo PD", "Solo Controlli"],
    horizontal=True, key="radio_eta",
)

if gruppo_eta == "Solo PD":
    df_eta = df[df["group"] == "PD"]
elif gruppo_eta == "Solo Controlli":
    df_eta = df[df["group"] == "Controllo"]
else:
    df_eta = df.copy()

with g1:
    fig = px.histogram(
        df_eta.dropna(subset=["Age"]),
        x="Age", color="group", nbins=20, opacity=0.70, barmode="overlay",
        color_discrete_map={"PD": PD_COL, "Controllo": CTRL_COL},
        labels={"Age": "Età (anni)", "group": "Gruppo"},
        title="Distribuzione Età · PD vs Control",
    )
    fig.add_vline(x=age_pd,   line_dash="dash", line_color="#2C7196",
                    annotation_text="μ PD",        annotation_font_size=10,
                    annotation_font_color="#2C7196", annotation_position="top right")
    fig.add_vline(x=age_ctrl, line_dash="dash", line_color="#8D8124",
                    annotation_text="μ CONTROLLI", annotation_font_size=10,
                    annotation_font_color="#8D8124", annotation_position="top right")
    fig.update_layout(yaxis_title="Numero partecipanti", height=450)
    fig.update_traces(marker_line_color="white", marker_line_width=1)
    st.plotly_chart(fig, width="stretch")

# Richiamo il file di test statistici per applicarli in questa sezione
esegui_test(
    grp_pd   = df_pd["Age"].dropna(),
    grp_ctrl = df_ctrl["Age"].dropna(),
    label    = "Età"
)

#  SEZIONE 2: visualizzazione MoCA Score
with st.expander("MoCA Score", expanded=False):
    st.caption(
        "Montreal Cognitive Assessment · "
        "disponibile per 47 controlli su 85 · non raccolto per i pazienti PD"
    )
    # Estrae i punteggi MoCA dei soli controlli, convertendoli in numerico ("-" diventa NaN) e scartando i valori mancanti
    ctrl_df_moca = df_ctrl.copy()
    ctrl_df_moca["MoCA Score"] = pd.to_numeric(ctrl_df_moca["MoCA Score"], errors="coerce")
    moca_vals = ctrl_df_moca["MoCA Score"].dropna()
    
    # Filtra i punteggi nell'intervallo clinico selezionato nella sidebar (Normale / MCI / Deterioro)
    r_min, r_max  = range_options[range_sel]
    moca_filtrata = moca_vals[moca_vals.between(r_min, r_max)]

    m1, m2, m3 = st.columns(3)
    m1.metric("Soggetti nell'intervallo", len(moca_filtrata))
    if len(moca_filtrata) > 0:
        m2.metric("Media",   f"{moca_filtrata.mean():.1f}")
        m3.metric("Mediana", f"{moca_filtrata.median():.0f}")

    fig = px.histogram(
        pd.DataFrame({"MoCA Score": moca_filtrata}),
        x="MoCA Score", nbins=13, color_discrete_sequence=[MOCA_COL],
        opacity=0.85, title=f"Distribuzione MoCA Score · {range_sel}",
        labels={"MoCA Score": "MoCA Score", "count": "N partecipanti"},
    )
    if len(moca_filtrata) > 0:
        fig.add_vline(x=moca_filtrata.mean(), line_dash="dash", line_color="#000000", line_width=1.8,
                      annotation_text=f"μ {moca_filtrata.mean():.1f}", annotation_font_size=10,
                      annotation_font_color="#000000", annotation_position="top left")
    for soglia, etichetta, colore in [
        (26, "Normale",   "#059669"),
        (18, "MCI",       "#F59E0B"),
        (17, "Deterioro", "#EF4444"),
    ]:
        fig.add_vline(x=soglia, line_dash="dot", line_color=colore, line_width=1.2,
                      annotation_text=etichetta, annotation_font_size=9,
                      annotation_font_color=colore, annotation_position="top right")
    fig.update_layout(xaxis_title="MoCA Score", yaxis_title="N partecipanti", height=450)
    fig.update_xaxes(range=[-0.5, 30.5])
    fig.update_traces(marker_line_color="white", marker_line_width=1)
    st.plotly_chart(fig, width="stretch")

#  SEZIONE 3: distribuzione indici UPDRS III tra PD e controlli
with st.expander("UPDRS III", expanded=False):
    st.caption("Confronto degli indici motori clinicamente rilevanti · PD vs Control")
    st.info(HELP_INDICI[indice_sel])

    if gruppo_sel == "Solo PD":
        df_box = df[df["group"] == "PD"]
    elif gruppo_sel == "Solo Controlli":
        df_box = df[df["group"] == "Controllo"]
    else:
        df_box = df.copy()

    fig = px.box(
        df_box.dropna(subset=[indice_sel]),
        x="group", y=indice_sel, color="group",
        color_discrete_map={"PD": PD_COL, "Controllo": CTRL_COL},
        points="all", title=INDICI[indice_sel],
        labels={"group": "", indice_sel: "Score (0-4)" if indice_sel != "UPDRS_III" else "Score (0-132)"},
    )
    fig.update_traces(jitter=0.3, marker=dict(size=4, opacity=0.5))

    if indice_sel == "UPDRS_III":
        val_max = df_box[indice_sel].max()
        fig.update_yaxes(range=[-2, val_max * 1.10])
    else:
        fig.update_yaxes(range=[-0.3, 4.3])

    fig.update_layout(height=480, showlegend=False)
    st.plotly_chart(fig, width='stretch')

    # Richiamo la funzione dei test statistici
    esegui_test(
        grp_pd   = df[df["group"] == "PD"][indice_sel].dropna(),
        grp_ctrl = df[df["group"] == "Controllo"][indice_sel].dropna(),
        label    = INDICI[indice_sel]
    )

#  SEZIONE 4: caratteristiche cliniche PD
with st.expander("Caratteristiche Cliniche · Solo Pazienti PD", expanded=False):
    st.caption("Stadio di malattia, DBS e confronto · solo pazienti PD")

    # Preparazione categorie DBS
    df_dbs = df_pd.copy()
    df_dbs["DBS?"] = df_dbs["DBS?"].replace("-", np.nan)
    df_dbs["Bilateral vs uilateral"] = df_dbs["Bilateral vs uilateral"].replace("-", np.nan)
    df_dbs["Bilateral vs uilateral"] = df_dbs["Bilateral vs uilateral"].str.strip()

    df_dbs["Categoria DBS"] = "Non dichiarato"
    df_dbs.loc[df_dbs["DBS?"] == "No", "Categoria DBS"] = "No DBS"
    df_dbs.loc[(df_dbs["DBS?"] == "Yes") & (df_dbs["Bilateral vs uilateral"] == "Bilateral"),      "Categoria DBS"] = "DBS Bilaterale"
    df_dbs.loc[(df_dbs["DBS?"] == "Yes") & (df_dbs["Bilateral vs uilateral"] == "Unilateral (R)"), "Categoria DBS"] = "DBS Unilaterale"

    colori_dbs = {
        "No DBS":          "#F4A6B5",
        "DBS Bilaterale":  "#DC143C",
        "DBS Unilaterale": "#E8748E",
        "Non dichiarato":  "#CAD1DD",
    }

    # Riga 1: H&Y stage (bar) + DBS (torta)
    col_hy, col_dbs = st.columns(2)

    with col_hy:
        hy = df_pd["Modified Hoehn & Yahr Score"].copy()
        hy = hy.replace("-", np.nan)
        hy = pd.to_numeric(hy, errors="coerce").dropna()

        hy_counts = hy.value_counts().sort_index().reset_index()
        hy_counts.columns = ["Stadio", "N pazienti"]
        hy_counts["Stadio"] = hy_counts["Stadio"].astype(str)

        fig = px.bar(
            hy_counts, x="Stadio", y="N pazienti", color="Stadio",
            color_discrete_sequence=["#FBD3DB", "#F4A6B5", "#E8748E", "#DC143C", "#B01030", "#7A0B21"],
            title="Hoehn & Yahr Stage", text="N pazienti",
        )
        fig.update_traces(textposition="outside", showlegend=False)
        fig.update_layout(xaxis_title="Stadio H&Y", yaxis_title="N pazienti", height=450, showlegend=False)
        st.plotly_chart(fig, width='stretch')

    with col_dbs:
        conteggi_dbs = df_dbs["Categoria DBS"].value_counts().reset_index()
        conteggi_dbs.columns = ["Categoria", "N pazienti"]

        fig = px.pie(
            conteggi_dbs, names="Categoria", values="N pazienti", hole=0.4, color="Categoria",
            color_discrete_map=colori_dbs, title="Deep Brain Stimulation (DBS)",
        )
        fig.update_traces(textinfo="label+percent", textfont_size=12)
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, width='stretch')

    # Confronto statistico H&Y · Con DBS vs Senza DBS
    st.markdown("---")
    st.markdown("**Confronto statistico · Stadio H&Y per gruppo DBS**")
    st.caption("Distribuzione dello stadio di malattia tra pazienti con e senza DBS.")

    df_hy_dbs = df_dbs[df_dbs["Categoria DBS"].isin(["No DBS", "DBS Bilaterale", "DBS Unilaterale"])].copy()
    df_hy_dbs["Gruppo DBS"] = np.where(df_hy_dbs["Categoria DBS"] == "No DBS", "Senza DBS", "Con DBS")
    df_hy_dbs["H&Y"] = pd.to_numeric(df_hy_dbs["Modified Hoehn & Yahr Score"].replace("-", np.nan), errors="coerce")
    df_hy_dbs = df_hy_dbs.dropna(subset=["H&Y"])

    fig = px.box(
        df_hy_dbs,
        x="Gruppo DBS", y="H&Y", color="Gruppo DBS",
        category_orders={"Gruppo DBS": ["Senza DBS", "Con DBS"]},
        color_discrete_map={"Senza DBS": "#F4A6B5", "Con DBS": "#DC143C"},
        points="all", title="Stadio Hoehn & Yahr · Con DBS vs Senza DBS",
        labels={"Gruppo DBS": "", "H&Y": "Stadio Hoehn & Yahr"},
    )
    fig.update_traces(jitter=0.3, marker=dict(size=5, opacity=0.5))
    fig.update_layout(height=450, showlegend=False)
    st.plotly_chart(fig, width='stretch')

    esegui_test(
        grp_pd   = df_hy_dbs[df_hy_dbs["Gruppo DBS"] == "Con DBS"]["H&Y"],
        grp_ctrl = df_hy_dbs[df_hy_dbs["Gruppo DBS"] == "Senza DBS"]["H&Y"],
        label    = "H&Y · Con vs Senza DBS"
    )