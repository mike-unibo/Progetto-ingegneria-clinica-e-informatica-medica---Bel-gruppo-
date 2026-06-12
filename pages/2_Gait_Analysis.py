import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import statsmodels.api as sm
from scipy.stats import ttest_ind, shapiro, mannwhitneyu, spearmanr

st.set_page_config(page_title="WearGait-PD · Gait analysis",layout="wide")

# ── TRADUZIONE TASK ──────────────────────────────────────────────────────────
TASK_IT = {
    "selfpace": "Passo normale",
    "hurriedpace": "Passo veloce",
}

def task_label(t: str) -> str:
    cleaned = str(t).lower().strip().replace("_", " ")
    return TASK_IT.get(cleaned, t.title())

# ── TRADUZIONE METRICHE ──────────────────────────────────────────────────────
METRIC_IT = {
    "Velocity_(cm./sec.)":           "Velocità (m/s)",
    "Stride_Length_(cm.).1":         "Lunghezza doppio passo (m) [Media]",
    "Step_Length_(cm.).1":           "Lunghezza passo (m) [Media]",
    "Absolute_Step_Length_(cm.).1":  "Lunghezza passo assoluta (m) [Media]",
    "Stride_Width_(cm.).1":          "Larghezza base appoggio (m) [Media]",
    "Swing_Time_(sec.).1":           "Tempo oscillazione (sec) [Media]",
    "Step_Ratio_(cm._x_min.).1":     "Rapporto passo/cadenza (m×min) [Media]",
    "Total_D._Support_%.1":          "Doppio appoggio totale % [Media]",
    "Initial_D._Support_%.1":        "Primo doppio appoggio % [Media]",
    "Terminal_D._Support_%.1":       "Secondo doppio appoggio % [Media]",
    "Stance_%.1":                    "Fase di appoggio % [Media]",
    "Ambulation_Time_(sec.)":        "Tempo di deambulazione (sec)",
    "SS_COP_Dist._(cm.).1":          "Distanza COP mono-appoggio (m) [Media]",
    "DS_COP_Dist._(cm.).1":          "Distanza COP doppio appoggio (m) [Media]",
    "Stance_COP_Dist._(cm.).1":      "Distanza COP stance totale (m) [Media]",
    "SS_COP_Path_Eff._%.1":          "Efficienza COP mono-appoggio % [Media]",
    "Step_Length_(cm.).3":           "Asimmetria nella lunghezza del passo tra i due lati (ASI).",
    "Stride_Width_(cm.).5":          "Variabilità della larghezza del passo (%CV).",
    "Integ._Pressure_(p_x_sec.).3":  "Asimmetria della pressione integrata tra i due lati (ASI).",
    "Single_Support_%.5":            "Variabilità del tempo di monopodalismo (%CV).",
    "Step_Time_(sec.).1":            "Tempo passo (sec) [Media]",
    "Step_Time_(sec.).5":            "Tempo passo (sec) [%CV]",
    "Toe_In/Out_Angle_(degrees).1":  "Angolo medico di extrarotazione/intrarotazione del piede (°).",
}

METRIC_HELP = {
    "Velocity_(cm./sec.)":              "Velocità media di cammino (m/s).",
    "Stride_Length_(cm.).1":            "Lunghezza media di un doppio passo (m).",
    "Step_Length_(cm.).1":              "Lunghezza media di un singolo passo (m).",
    "Absolute_Step_Length_(cm.).1":     "Lunghezza assoluta del passo, indipendente dal lato (m).",
    "Stride_Width_(cm.).1":             "Larghezza della base di appoggio tra i due piedi (m).",
    "Swing_Time_(sec.).1":              "Durata media della fase di oscillazione (sec).",
    "Step_Ratio_(cm._x_min.).1":        "Rapporto lunghezza passo / cadenza (m×min).",
    "Total_D._Support_%.1":             "Percentuale del ciclo trascorsa in doppio appoggio totale.",
    "Initial_D._Support_%.1":           "Percentuale del ciclo nel primo doppio appoggio.",
    "Terminal_D._Support_%.1":          "Percentuale del ciclo nel secondo doppio appoggio.",
    "Stance_%.1":                       "Percentuale del ciclo di passo in fase di appoggio.",
    "Ambulation_Time_(sec.)":           "Tempo totale necessario per percorrere il tappeto.",
    "SS_COP_Dist._(cm.).1":             "Distanza percorsa dal COP durante il singolo appoggio (m).",
    "DS_COP_Dist._(cm.).1":             "Distanza percorsa dal COP durante il doppio appoggio (m).",
    "Stance_COP_Dist._(cm.).1":         "Distanza totale del COP durante l'intera fase di stance (m).",
    "SS_COP_Path_Eff._%.1":             "Efficienza del percorso COP nel singolo appoggio (%).",
    "Step_Length_(cm.).3":              "Asimmetria nella lunghezza del passo tra i due lati (ASI).",
    "Stride_Width_(cm.).5":             "Variabilità della larghezza del passo (%CV).",
    "Integ._Pressure_(p_x_sec.).3":     "Asimmetria della pressione integrata tra i due lati (ASI).",
    "Single_Support_%.5":               "Variabilità del tempo di monopodalismo (%CV).",
    "Step_Time_(sec.).1":               "Durata media di un singolo passo (sec).",
    "Step_Time_(sec.).5":               "Variabilità della durata del passo (%CV).",
    "Toe_In/Out_Angle_(degrees).1":     "Angolo medico di extrarotazione/intrarotazione del piede (°).",
}

_WANT = list(METRIC_IT.keys())
CM_COLS = {"Velocity_(cm./sec.)", "Stride_Length_(cm.).1", "Step_Length_(cm.).1", "Absolute_Step_Length_(cm.).1", "Stride_Width_(cm.).1", "Step_Ratio_(cm._x_min.).1", "SS_COP_Dist._(cm.).1", "DS_COP_Dist._(cm.).1", "Stance_COP_Dist._(cm.).1"}

def _label(c: str) -> str:
    return METRIC_IT.get(c, c)

# ── CONFIGURAZIONE COLORI UNIFICATA ──────────────────────────────────────────
COLOR_MAP = {"PD": "crimson", "Control": "royalblue"}
COMBINED_COLORS = {
    "PD — M": "crimson", "PD — F": "salmon",
    "Control — M": "royalblue", "Control — F": "skyblue",
    "Invalidi": "darkgray"
}
ORDER_GRUPPI = ["PD", "Control"]

# ── CARICA E PULISCI DATI ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(r"dataset\tappeto+demographic.csv", sep=";", skiprows=[1], decimal=",", header=0)
    df.columns = df.columns.str.strip()
    df["Task"] = df["Task"].astype(str).str.strip().str.lower().str.replace(r"\s+", " ", regex=True).str.replace("_", " ")
    df = df[df["Task"] != "selfpace doorpat"]

    for col in ["Age", "Weight"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].where(df[col] > 0, np.nan)

    df["Height"] = df["Height"].replace(r"^\s*$", np.nan, regex=True)
    df["Height"] = pd.to_numeric(df["Height"], errors="coerce")
    df["Height"] = (df["Height"] * 0.0254).where(df["Height"].notna() & (df["Height"] > 0), np.nan)
    df["Sex"] = df["Sex"].astype(str).str.strip().where(df["Sex"].str.strip().isin(["Male", "Female"]), np.nan)
    return df

df_raw = load_data()
selected_cols = list(dict.fromkeys(c for c in _WANT if c in df_raw.columns))
df_all = df_raw.copy()
for c in selected_cols:
    if c in CM_COLS:
        df_all[c] = pd.to_numeric(df_all[c], errors="coerce") / 100

metric_labels = {c: _label(c) for c in selected_cols}
task_options_raw = sorted(df_all["Task"].dropna().unique())
task_options_labels = [task_label(t) for t in task_options_raw]

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    task_idx = st.selectbox("Seleziona Task:", range(len(task_options_raw)), format_func=lambda i: task_options_labels[i])
    task = task_options_raw[task_idx]

    metric = st.selectbox("Seleziona Metrica:", selected_cols, format_func=lambda c: metric_labels[c])
    st.caption(METRIC_HELP.get(metric, ""))

    st.subheader("Filtraggio dati:")
    with st.expander("Filtri", expanded=False):
        group_filter = st.radio("Gruppo:", ["PD", "Control", "Entrambi"], index=2, horizontal=False)
        sex_filter = st.radio("Sesso:", ["Maschio", "Femmina", "Entrambi"], index=2, horizontal=False)

        valid_ages = df_all["Age"][(df_all["Age"] > 0) & (df_all["Age"] < 100)].dropna()
        age_min, age_max = (int(valid_ages.min()), int(valid_ages.max())) if not valid_ages.empty else (0, 100)
        age_range = st.slider("Età (anni):", age_min, age_max, (age_min, age_max))

        balanced_n = st.number_input("Numero soggetti per gruppo (opzionale)", min_value=0, value=0, step=1, help="Seleziona un egual numero di soggetti per ciascun gruppo segliendo i soggetti più vicini alla media dell'età del campione filtato.")
        use_balanced = balanced_n > 0
        

# ── APPLICA FILTRI GLOBALI ──────────────────────────────────────────────────
def apply_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Age"].isna() | ((df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1]))]
    if group_filter == "PD":
        df = df[df["PD_vs_Control"] == "PD"]
    elif group_filter == "Control":
        df = df[df["PD_vs_Control"] == "Control"]
    if sex_filter == "Maschi":
        df = df[df["Sex"] == "Male"]
    elif sex_filter == "Femmine":
        df = df[df["Sex"] == "Female"]
    return df

df_filtered = apply_global_filters(df_all.copy())
df_task = df_filtered[df_filtered["Task"] == task].copy()
df_task[metric] = pd.to_numeric(df_task[metric], errors="coerce")

# ── IDENTIFICAZIONE ANOMALIE ED ESCLUSIONI ───────────────────────────────────
df_missing_metric = df_task[df_task[metric].isna() | (df_task[metric] == 0)].copy()
df_valid_metric = df_task.dropna(subset=[metric, "PD_vs_Control"])
df_valid_metric = df_valid_metric[df_valid_metric[metric] != 0].copy()
df_valid_metric["BMI"] = df_valid_metric["Weight"] / (df_valid_metric["Height"] ** 2)

demo_null_rows = []
anomalo_fisico_rows = []

for idx, row in df_valid_metric.iterrows():
    age, height, weight, sex, bmi = row["Age"], row["Height"], row["Weight"], row["Sex"], row["BMI"]
    if pd.isna(age) or pd.isna(height) or pd.isna(weight) or pd.isna(sex):
        demo_null_rows.append(idx)
        continue
    reasons = []
    if age > 110: reasons.append("Età fuori range (>110)")
    if age < 18:
        if bmi < 10 or bmi > 40: reasons.append(f"BMI anomalo bambino ({bmi:.1f})")
        if height < 0.50 or height > 2.10: reasons.append(f"Altezza anomala bambino ({height:.2f} m)")
    else:
        if bmi < 14 or bmi > 45: reasons.append(f"BMI anomalo ({bmi:.1f})")
        if height < 1.30 or height > 2.30: reasons.append(f"Altezza anomala adulto ({height:.2f} m)")
    if reasons:
        df_valid_metric.at[idx, "anomalie_descr"] = " | ".join(reasons)
        anomalo_fisico_rows.append(idx)

df_demo_nulli = df_valid_metric.loc[demo_null_rows].copy()
df_campioni_anomali = df_valid_metric.loc[anomalo_fisico_rows].copy()
df_plot = df_valid_metric.drop(index=demo_null_rows).copy()

# Calcolo campioni disponibili per gruppo prima del bilanciamento per i controlli di errore
grp_counts = df_plot.groupby("PD_vs_Control")[metric].count()
min_available = int(grp_counts.min()) if len(grp_counts) > 0 else 0

# 1. ERRORE NUMERICO SE IL BILANCIAMENTO SUPERA I SOGGETTI DISPONIBILI
if use_balanced and int(balanced_n) > min_available:
    st.sidebar.error(f"Errore: Il numero richiesto ({balanced_n}) supera la dimensione del gruppo più piccolo ({min_available}).")
    st.error(f"Non è possibile generare l'analisi. Il valore inserito per il bilanciamento del campione ({balanced_n}) è superiore al numero di soggetti presenti nel gruppo più piccolo ({min_available}). Riduci il valore nella barra laterale.")
    st.stop()

# ── CAMPIONE BILANCIATO ───────────────────────────────────────────────────────
if use_balanced and not df_plot.empty:
    n_bal = min(int(balanced_n), min_available)

    if n_bal >= 1:

        def closest_to_mean_age(df_grp, k):
            target_age = sum(age_range) / 2 

            df_grp = df_grp.dropna(subset=["Age"])

            distances = (df_grp["Age"] - target_age).abs()

            return df_grp.loc[
                distances.nsmallest(min(k, len(df_grp))).index
            ]

        balanced_parts = []

        for grp in ORDER_GRUPPI:
            df_grp = df_plot[df_plot["PD_vs_Control"] == grp]
            if not df_grp.empty:
                balanced_parts.append(closest_to_mean_age(df_grp, n_bal))

        df_plot = pd.concat(balanced_parts) if balanced_parts else df_plot.iloc[0:0]

# ── LABEL METRICA CORRENTE ────────────────────────────────────────────────────
current_metric_label = metric_labels[metric]
current_task_label = task_label(task)

# 2. ERRORE SE NON RIMANGONO SOGGETTI DOPO IL FILTRAGGIO
if df_plot.empty:
    st.error(f"Non risultano soggetti validi per la visualizzazione della metrica ({current_metric_label}), prova a modificare la sezione: Filtraggio dati")
    st.stop()

# ── INTERFACCIA PRINCIPALE ───────────────────────────────────────────────────
st.title("Gait Analysis", text_alignment="center")
st.write("La gait analysis utilizza un tappeto sensorizzato che registra automaticamente il modo in cui il soggetto cammina.\n\n Ogni appoggio del piede viene rilevato e trasformato in dati numerici per il confronto tra soggetti sani e pazienti con Parkinson.")
st.markdown("<hr style='border-top: 3px solid green; margin-top: -5px;'>", unsafe_allow_html=True)

st.subheader(f"Task: {current_task_label}")

filt_total = len(df_task)
filt_pd = (df_plot["PD_vs_Control"] == "PD").sum()
filt_ctrl = (df_plot["PD_vs_Control"] == "Control").sum()
count_cammino_nulli = len(df_missing_metric)
count_demo_nulli = len(df_demo_nulli)
count_anomali = len(df_campioni_anomali)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Campioni ottenuti:", filt_total, border=True)
k2.metric("Campioni Control:", filt_ctrl, border=True)
k3.metric("Campioni PD:", filt_pd, border=True)
k4.metric("Campioni con dati nulli:", count_demo_nulli, border=True)

if count_cammino_nulli > 0 or count_demo_nulli > 0 or count_anomali > 0:
    with st.expander("Mostra dettagli righe escluse o problematiche", expanded=False):
        if count_cammino_nulli > 0:
            st.markdown("**Soggetti con dati cammino nulli o zero (Esclusi):**")
            df_missing_disp = df_missing_metric[["Participant_ID", "PD_vs_Control", "Sex", "Age"]].reset_index(drop=True)
            df_missing_disp.index += 1
            st.dataframe(df_missing_disp, width='stretch')
        if count_demo_nulli > 0:
            st.markdown("**Soggetti con valori demografici nulli/mancanti (Esclusi):**")
            df_demo_disp = df_demo_nulli[["Participant_ID", "PD_vs_Control", "Age", "Height", "Weight", "Sex"]].reset_index(drop=True)
            df_demo_disp.index += 1
            st.dataframe(df_demo_disp, width='stretch')
        if count_anomali > 0:
            st.markdown("**Campioni anomali rilevati (Inclusi nell'analisi statistica):**")
            disp_anomali = df_campioni_anomali.copy()
            disp_anomali["Height_m"] = disp_anomali["Height"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
            df_anomali_disp = disp_anomali[["Participant_ID", "PD_vs_Control", "Age", "Height_m", "Weight", "BMI", "Sex", "anomalie_descr"]].reset_index(drop=True)
            df_anomali_disp.index += 1
            st.dataframe(df_anomali_disp, width='stretch')

totale_iniziale_task = len(df_all[df_all["Task"] == task])
totale_dopo_filtri = len(df_task)
campioni_esclusi = totale_iniziale_task - totale_dopo_filtri

st.info(f"Sono stati filtrati {campioni_esclusi} campioni")

comp_col, age_col = st.columns(2)

with comp_col:
    pie_data = []
    df_pd_f = df_plot[df_plot["PD_vs_Control"] == "PD"]
    df_ctrl_f = df_plot[df_plot["PD_vs_Control"] == "Control"]
    for grp, df_grp in [("PD", df_pd_f), ("Control", df_ctrl_f)]:
        for sex in ["Male", "Female"]:
            n = (df_grp["Sex"] == sex).sum()
            if n > 0:
                pie_data.append({"Categoria": f"{grp} — {'M' if sex=='Male' else 'F'}", "N": n})
    totale_nulli = count_cammino_nulli + count_demo_nulli
    if totale_nulli > 0:
        pie_data.append({"Categoria": "Invalidi", "N": totale_nulli})
    df_pie = pd.DataFrame(pie_data)
    fig_pie = px.pie(
        df_pie, 
        names="Categoria", 
        values="N", 
        color="Categoria", 
        color_discrete_map=COMBINED_COLORS,
        title="Composizione del campione", 
        hole=0.35, 
        category_orders={"Categoria": list(COMBINED_COLORS.keys())})
    fig_pie.update_traces(texttemplate="%{label}<br>%{percent}")
    fig_pie.update_layout(showlegend=True, legend=dict(orientation="h"))
    st.plotly_chart(fig_pie, width='stretch')

with age_col:
    df_age = df_filtered[df_filtered["PD_vs_Control"].isin(["PD", "Control"])].dropna(subset=["Age"])
    mean_age_pd = df_age[df_age["PD_vs_Control"] == "PD"]["Age"].mean()
    mean_age_ctrl = df_age[df_age["PD_vs_Control"] == "Control"]["Age"].mean()
    age_diff = abs(mean_age_pd - mean_age_ctrl) if not (pd.isna(mean_age_pd) or pd.isna(mean_age_ctrl)) else None
    fig_age = px.histogram(
        df_age, 
        x="Age", 
        color="PD_vs_Control", 
        nbins=20, 
        barmode="group", 
        color_discrete_map=COLOR_MAP,
        category_orders={"PD_vs_Control": ORDER_GRUPPI},
        labels={"Age": "Età (anni)"}, 
        title="Distribuzione età per gruppo")
    fig_age.update_layout(template="simple_white", yaxis=dict(showgrid=True), legend_title_text="")
    st.plotly_chart(fig_age, width='stretch')
    if age_diff is not None:
        if age_diff > 5: st.warning(f"Differenza età media: {age_diff:.1f} anni\n\nControl: {mean_age_ctrl:.1f} anni · PD: {mean_age_pd:.1f} anni")
        else: st.success(f"Differenza età media: {age_diff:.1f} anni\n\nControl: {mean_age_ctrl:.1f} anni · PD: {mean_age_pd:.1f} anni")

# ── VIOLIN PLOT & TABELLA METRICHE ───────────────────────────────────────────
with st.expander("VIOLIN PLOT" , expanded=False):
    st.title(f"Violin Plot {current_metric_label} per gruppo")
    st.caption(f"Mostra la distribuzione del valori per PD e Control nel task *{current_task_label}* \n\n box = mediana e quartili, puntini = singoli soggetti.")
    
    fig = px.violin(df_plot, x="PD_vs_Control", y=metric, color="PD_vs_Control", box=True, points="all",
                    color_discrete_map=COLOR_MAP, category_orders={"PD_vs_Control": ORDER_GRUPPI},
                    labels={metric: current_metric_label, "PD_vs_Control": "Gruppo"})
    fig.update_traces(hoverinfo="all", selector=dict(type="violin"))
    fig.update_layout(showlegend=True, yaxis=dict(showgrid=True, gridcolor="LightGray"), legend_title_text="")
    st.plotly_chart(fig, width='stretch')

    metrics_list = []
    for group in ORDER_GRUPPI:
        col = df_plot[df_plot["PD_vs_Control"] == group][metric]
        if len(col) != 0:
            mean = col.mean()
            median = col.median()
            q1 = col.quantile(0.25)
            q3 = col.quantile(0.75)
            iqr = q3 - q1
            std = col.std()
            n_outliers = len(col[(col < q1 - 1.5 * iqr) | (col > q3 + 1.5 * iqr)])

            metrics_list.append({
                "Gruppo": group,
                "Mediana": round(median, 3),
                "Media": round(mean, 3),
                "Deviazione Std": round(std, 3),
                "IQR": round(iqr, 3),
                "Outliers": n_outliers,
            })

    if metrics_list:
        df_metrics = pd.DataFrame(metrics_list)
        st.dataframe(
            df_metrics,
            column_config={
                "IQR": st.column_config.NumberColumn(
                    "IQR",
                    help="Interquantile Range(Q3 - Q1) \n\n Misura la dispersione del 50% centrale dei dati.",
                )
            },
            hide_index=True,
            width='stretch',
        )

# ── ISTOGRAMMA ────────────────────────────────────────────────────────────────
with st.expander("ISTOGRAMMA", expanded=False):
    st.title(f"Istogramma {current_metric_label} per gruppo")
    st.caption(f"Mostra la frequenza dei valori della metrica per i due gruppi")
    fig = px.histogram(df_plot, x=metric, color="PD_vs_Control", nbins=25, barmode="group", color_discrete_map=COLOR_MAP,
                       category_orders={"PD_vs_Control": ORDER_GRUPPI},
                       labels={metric: current_metric_label, "PD_vs_Control": "Gruppo"})
    fig.update_layout(template="simple_white", yaxis=dict(showgrid=True), legend_title_text="")
    st.plotly_chart(fig, width='stretch')

# ── TEST STATISTICO ──────────────────────────────────────────────────────────
with st.expander("TEST STATISTICO: PD vs Control", expanded=False):
    st.title(f"Test statistico per la metrica: {current_metric_label} ")
    st.caption(f"Confronto statistico di **{current_metric_label}** tra PD e Control nel task *{current_task_label}*. La normalità viene verificata con Shapiro-Wilk per scegliere il test appropriato.")

    g_pd   = df_plot[df_plot["PD_vs_Control"] == "PD"][metric].dropna()
    g_ctrl = df_plot[df_plot["PD_vs_Control"] == "Control"][metric].dropna()

    if len(g_pd) > 1 and len(g_ctrl) > 1:
        sw_ctrl_p = shapiro(g_ctrl.sample(min(len(g_ctrl), 1000), random_state=42))[1] if len(g_ctrl) >= 3 else 0
        sw_pd_p   = shapiro(g_pd.sample(min(len(g_pd), 1000), random_state=42))[1]     if len(g_pd)   >= 3 else 0
        all_normal = (sw_ctrl_p >= 0.05) and (sw_pd_p >= 0.05)

        col_sw1, col_sw2 = st.columns(2)
        col_sw1.metric(
            label="Shapiro-Wilk PD",
            value=f"p = {sw_pd_p:.4f}",
            delta="Normale" if sw_pd_p >= 0.05 else "Non normale",
            delta_color="normal" if sw_pd_p >= 0.05 else "inverse",
        )
        col_sw2.metric(
            label="Shapiro-Wilk Control",
            value=f"p = {sw_ctrl_p:.4f}",
            delta="Normale" if sw_ctrl_p >= 0.05 else "Non normale",
            delta_color="normal" if sw_ctrl_p >= 0.05 else "inverse",
        )

        def _iqr_outliers(s):
            Q1, Q3 = s.quantile(0.25), s.quantile(0.75)
            IQR = Q3 - Q1
            return ((s < Q1 - 1.5 * IQR) | (s > Q3 + 1.5 * IQR)).sum()

        outlier_present = (_iqr_outliers(g_ctrl) > 0) or (_iqr_outliers(g_pd) > 0)

        if not all_normal or outlier_present:
            st.warning("Almeno uno dei gruppi rifiuta la normalità (p < 0.05) o presenta outlier. Il test non parametrico (Mann-Whitney U) è consigliato.")
        else:
            st.success("Entrambi i gruppi sono normalmente distribuiti (p ≥ 0.05) e privi di outlier. Il test parametrico (Welch's T-test) è consigliato.")

        if all_normal and not outlier_present:
            test = st.segmented_control("**Test:**", ["Welch's T-test", "Mann-Whitney U test"], default="Welch's T-test", width="stretch")
        else:
            test = st.segmented_control("**Test:**", ["Welch's T-test", "Mann-Whitney U test"], default="Mann-Whitney U test", width="stretch")

        t_stat, t_p = ttest_ind(g_ctrl, g_pd, equal_var=False, nan_policy="omit")
        u_stat, u_p = mannwhitneyu(g_ctrl, g_pd, alternative="two-sided")

        # Calcolo dei parametri per capire la direzione della differenza
        mean_ctrl, mean_pd = g_ctrl.mean(), g_pd.mean()
        med_ctrl, med_pd = g_ctrl.median(), g_pd.median()

        c1, c2, c3 = st.columns(3)
        
        if test == "Welch's T-test":
            with c1:
                st.metric("t-statistic", f"{t_stat:.5f}")
            with c2:
                st.metric("p-value", f"{t_p:.5f}")
            with c3:
                st.write(" ")
                if t_p < 0.05:
                    if mean_ctrl > mean_pd:
                        st.success("Differenza significativa: **Control > PD**")
                    else:
                        st.success("Differenza significativa: **PD > Control**")
                else:
                    st.info("Differenza non significativa")
                    
        else:
            with c1:
                st.metric("U statistic", f"{u_stat:.5f}")
            with c2:
                st.metric("p-value", f"{u_p:.5f}")
            with c3:
                st.write(" ")
                if u_p < 0.05:
                    if med_ctrl > med_pd:
                        st.success("Differenza significativa: **Control > PD**")
                    else:
                        st.success("Differenza significativa: **PD > Control**")
                else:
                    st.info("Differenza non significativa")
    else:
        st.warning("Dati insufficienti per effettuare i test statistici.")
          
# ── SCATTER PLOT ─────────────────────────────────────────────────────────────
with st.expander("SCATTER PLOT", expanded=False):
    st.title(f"Scatter plot: {current_metric_label} vs Dati Demografici")
    st.caption(f"Analisi della correlazione tra **{current_metric_label}** e variabili demografiche nel task *{current_task_label}*.")
    demo_var = st.selectbox(
        "Seleziona la variabile demografica per l'asse X:",
        ["Age", "Height", "Weight"],
        index=0,
        format_func=lambda v: {"Age": "Età (anni)", "Height": "Altezza (m)", "Weight": "Peso (kg)"}[v]
    )
    demo_label = {"Age": "Età (anni)", "Height": "Altezza (m)", "Weight": "Peso (kg)"}[demo_var]

    df_sc = df_plot.copy()
    df_sc[demo_var] = pd.to_numeric(df_sc[demo_var], errors="coerce")
    df_sc = df_sc.dropna(subset=[demo_var, metric])

    if not df_sc.empty:
        fig_scatter = px.scatter(
            df_sc, x=demo_var, y=metric, color="PD_vs_Control", trendline="ols",
            color_discrete_map=COLOR_MAP, category_orders={"PD_vs_Control": ORDER_GRUPPI},
            labels={demo_var: demo_label, metric: current_metric_label},
            title=f"{current_metric_label} vs {demo_label} — {current_task_label}",
            template="simple_white",
            hover_data={"Age": True, "Height": True, "Weight": True, "Sex": True}
        )
        fig_scatter.update_traces(marker=dict(size=8))
        fig_scatter.update_layout(
            yaxis=dict(showgrid=True, gridcolor="LightGray"),
            legend_title_text=""
        )
        st.plotly_chart(fig_scatter, width='stretch')

        rows = []
        for g in ORDER_GRUPPI:
            sub = df_sc[df_sc["PD_vs_Control"] == g]
            if len(sub) >= 3:
                rho, p_rho = spearmanr(sub[demo_var], sub[metric])
                X = sm.add_constant(sub[demo_var])
                ols = sm.OLS(sub[metric], X).fit()
                slope = ols.params.iloc[1]
                rows.append({
                    "Gruppo": g, 
                    "Spearman ρ": round(rho, 3), 
                    "p-value": f"{p_rho:.4f}", 
                    "Pendenza OLS": round(slope, 4)
                })
                
        if rows:
            df_scatter_res = pd.DataFrame(rows).set_index("Gruppo")
            st.dataframe(
                df_scatter_res,
                column_config={
                    "Spearman ρ": st.column_config.NumberColumn(
                        "Spearman ρ",
                        help=(
                            "Misura la forza e la direzione della relazione tra la variabile demografica e la metrica del cammino.\n\n"
                            "• Vicino a -1: Forte relazione inversa.\n\n"
                            "• Vicino a 0: Nessuna relazione.\n\n"
                            "• Vicino a +1: Forte relazione diretta."
                        )
                    ),
                    "p-value": st.column_config.TextColumn(
                        "p-value",
                        help="Indica l'affidabilità statistica della correlazione di Spearman. Se è inferiore a 0.05, il legame è scientificamente significativo."
                    ),
                    "Pendenza OLS": st.column_config.NumberColumn(
                        "Pendenza OLS",
                        help="Inclinazione della retta di regressione calcolata con i Minimi Quadrati Ordinari."
                    )
                },
                width='stretch'
            )

    else:
        st.warning("Dati insufficienti per generare lo scatter plot.")