import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
from test_statistici import esegui_test

#  PAGE CONFIG
st.set_page_config(page_title="WearGait-PD · Dati Demografici", page_icon="icon.png", layout="wide")

# Colori usati nei grafici
#PD_COL   = "#83CFF8"
PD_COL = "crimson"
#CTRL_COL = "#EED93A"
CTRL_COL = "royalblue"
MALE_COL = "#728FFA"
FEM_COL  = "#FA729F"
MOCA_COL = "royalblue"

# Dizionario indici UPDRS — chiave = nome colonna nel CSV, valore = nome leggibile
INDICI = {
    "UPDRS_III":         "UPDRS III — Punteggio Totale (0–132)",
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

HELP_INDICI = {
    "UPDRS_III":         "Somma dei 33 sotto-item della parte motoria dell'MDS-UPDRS. Valori più alti indicano maggiore compromissione motoria. Range: 0–132.",
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

#  CARICAMENTO DATI
@st.cache_data(show_spinner=False)
def load():
    pd_df   = pd.read_csv("dataset/PD - Demographic+Clinical - datasetV1.csv", header=1)
    ctrl_df = pd.read_csv("dataset/CONTROLS - Demographic+Clinical - datasetV1.csv", header=1)
    pd_df.rename(columns={"Age (years)": "Age"}, inplace=True)

    for colonna in colonne_updrs:
        pd_df[colonna]   = pd.to_numeric(pd_df[colonna],   errors="coerce")
        ctrl_df[colonna] = pd.to_numeric(ctrl_df[colonna], errors="coerce")

    pd_df["UPDRS_III"]   = pd_df[colonne_updrs].sum(axis=1, min_count=len(colonne_updrs)//2)
    ctrl_df["UPDRS_III"] = ctrl_df[colonne_updrs].sum(axis=1, min_count=len(colonne_updrs)//2)

    pd_df["group"]   = "PD"
    ctrl_df["group"] = "Controllo"

    for df in [pd_df, ctrl_df]:
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
        df["Sex"] = df["Sex"].replace("-", np.nan)

    return pd.concat([pd_df, ctrl_df], ignore_index=True)

df      = load()
df_pd   = df[df["group"] == "PD"]
df_ctrl = df[df["group"] == "Controllo"]

# Statistiche di base
N_PD   = len(df_pd)
N_CTRL = len(df_ctrl)
N_TOT  = N_PD + N_CTRL

age_pd   = df_pd["Age"].mean()
age_ctrl = df_ctrl["Age"].mean()

def sex_counts(sub):
    vc = sub["Sex"].value_counts()
    return int(vc.get("Male", 0)), int(vc.get("Female", 0))

m_pd,   f_pd   = sex_counts(df_pd)
m_ctrl, f_ctrl = sex_counts(df_ctrl)
m_tot          = m_pd + m_ctrl
f_tot          = f_pd + f_ctrl

#  SIDEBAR — filtri interattivi
with st.sidebar:
    st.markdown("### MoCA Score")
    range_options = {
        "Tutti (0–30)":    (0,  30),
        "Normale (26–30)": (26, 30),
        "MCI (18–25)":     (18, 25),
        "Deterioro (≤17)": (0,  17),
    }
    range_sel = st.selectbox("Intervallo MoCA", options=list(range_options.keys()))

    st.markdown("---")
    st.markdown("### Indici UPDRS III")
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

#  INTESTAZIONE
st.title("WearGait-PD · Panoramica del Dataset")
st.caption(
    f"Dataset open-access per lo studio del cammino nella malattia di Parkinson · "
    f"{N_TOT} partecipanti · Johns Hopkins / FDA / VA Seattle"
)
st.divider()

#  KPI
st.subheader("Riepilogo del Campione")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Partecipanti totali",      N_TOT,             border=True)
c2.metric("Pazienti PD",              N_PD,              border=True)
c3.metric("Controlli",                N_CTRL,            border=True)
c4.metric("Età media PD (aa)",        f"{age_pd:.0f}",   border=True)
c5.metric("Età media Controlli (aa)", f"{age_ctrl:.0f}", border=True)
st.divider()

#  SEZIONE 1 — Distribuzione del Campione
st.markdown("##### Distribuzione del Campione")
# with st.expander("Distribuzione del Campione e test statistici per età", expanded=False):
g1, g2 = st.columns([2, 1])

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
        title="Distribuzione Età · PD vs Controls",
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

esegui_test(
    grp_pd   = df_pd["Age"].dropna(),
    grp_ctrl = df_ctrl["Age"].dropna(),
    label    = "Età"
)

#  SEZIONE 2 — MoCA Score
with st.expander("MoCA Score", expanded=False):
    st.caption(
        "Montreal Cognitive Assessment · "
        "disponibile per 47 controlli su 85 · non raccolto per i pazienti PD"
    )

    ctrl_df_moca = df_ctrl.copy()
    ctrl_df_moca["MoCA Score"] = pd.to_numeric(ctrl_df_moca["MoCA Score"], errors="coerce")
    moca_vals = ctrl_df_moca["MoCA Score"].dropna()

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

#  SEZIONE 3 — UPDRS III
with st.expander("UPDRS III", expanded=False):
    st.caption("Confronto degli indici motori clinicamente rilevanti · PD vs Controlli")
    #st.info(HELP_INDICI[indice_sel])
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
        labels={"group": "", indice_sel: "Score (0–4)" if indice_sel != "UPDRS_III" else "Score (0–132)"},
    )
    fig.update_traces(jitter=0.3, marker=dict(size=4, opacity=0.5))

    if indice_sel == "UPDRS_III":
        val_max = df_box[indice_sel].max()
        fig.update_yaxes(range=[-2, val_max * 1.10])
    else:
        fig.update_yaxes(range=[-0.3, 4.3])

    fig.update_layout(height=480, showlegend=False)
    st.plotly_chart(fig, width='stretch')
    
    esegui_test(
        grp_pd   = df[df["group"] == "PD"][indice_sel].dropna(),
        grp_ctrl = df[df["group"] == "Controllo"][indice_sel].dropna(),
        label    = INDICI[indice_sel]
    )

#  SEZIONE 4 — Caratteristiche Cliniche PD
with st.expander("Caratteristiche Cliniche · Solo Pazienti PD", expanded=False):
    st.caption("Stadio di malattia, DBS e fisioterapia · solo pazienti PD (n=100)")
    # grafico H&Y 

    hy = df_pd["Modified Hoehn & Yahr Score"].copy()
    hy = hy.replace("-", np.nan)
    hy = pd.to_numeric(hy, errors="coerce").dropna()

    hy_counts = hy.value_counts().sort_index().reset_index()
    hy_counts.columns = ["Stadio", "N pazienti"]
    hy_counts["Stadio"] = hy_counts["Stadio"].astype(str)

    fig = px.bar(
        hy_counts, x="Stadio", y="N pazienti", color="Stadio",
        color_discrete_sequence=["#BFDBFE", "#93C5FD", "#60A5FA", "#3B82F6", "#1D4ED8", "#1E3A5F"],
        title="Hoehn & Yahr Stage", text="N pazienti",
    )
    fig.update_traces(textposition="outside", showlegend=False)
    fig.update_layout(xaxis_title="Stadio H&Y", yaxis_title="N pazienti", height=450, showlegend=False)
    st.plotly_chart(fig, width="stretch")

    # grafico DBS e FT
    col_b, col_c = st.columns(2)
    with col_b:
        df_dbs = df_pd.copy()
        df_dbs["DBS?"] = df_dbs["DBS?"].replace("-", np.nan)
        df_dbs["Bilateral vs uilateral"] = df_dbs["Bilateral vs uilateral"].replace("-", np.nan)
        df_dbs["Bilateral vs uilateral"] = df_dbs["Bilateral vs uilateral"].str.strip()

        df_dbs["Categoria DBS"] = "Non dichiarato"
        df_dbs.loc[df_dbs["DBS?"] == "No", "Categoria DBS"] = "No DBS"
        df_dbs.loc[(df_dbs["DBS?"] == "Yes") & (df_dbs["Bilateral vs uilateral"] == "Bilateral"),      "Categoria DBS"] = "DBS Bilaterale"
        df_dbs.loc[(df_dbs["DBS?"] == "Yes") & (df_dbs["Bilateral vs uilateral"] == "Unilateral (R)"), "Categoria DBS"] = "DBS Unilaterale"

        conteggi_dbs = df_dbs["Categoria DBS"].value_counts().reset_index()
        conteggi_dbs.columns = ["Categoria", "N pazienti"]

        colori_dbs = {
            "No DBS":          "#BFDBFE",
            "DBS Bilaterale":  "#2563EB",
            "DBS Unilaterale": "#60A5FA",
            "Non dichiarato":  "#CAD1DD",
        }
        fig = px.pie(
            conteggi_dbs, names="Categoria", values="N pazienti", hole=0.4, color="Categoria",
            color_discrete_map=colori_dbs, title="Deep Brain Stimulation (DBS)",
        )
        fig.update_traces(textinfo="label+percent", textfont_size=12)
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, width='stretch')

    with col_c:
        ptot = df_pd["PT/OT status"].str.strip().replace("-", np.nan).dropna()
        ptot_counts = ptot.value_counts().reset_index()
        ptot_counts.columns = ["Risposta", "N pazienti"]

        fig = px.pie(
            ptot_counts, names="Risposta", values="N pazienti", hole=0.4, color="Risposta",
            color_discrete_map={"Yes": "#83CFF8", "No": "#F7E28E"},
            title="Fisioterapia / Terapia Occupazionale (PT/OT)",
        )
        fig.update_traces(textinfo="label+percent", textfont_size=12)
        fig.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig, width='stretch')
