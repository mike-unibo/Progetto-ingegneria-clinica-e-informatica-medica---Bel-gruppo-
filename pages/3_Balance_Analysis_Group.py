import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import ttest_ind, shapiro, mannwhitneyu, spearmanr
import statsmodels.api as sm

st.set_page_config(layout="wide")
# ── CONFIGURAZIONE COLORI UNIFICATA ──────────────────────────────────────────
COLOR_MAP = {"PD": "crimson", "Control": "royalblue"}

# Palette combinata per Grafico a Torta e Scatter Plot quando il sesso è separato
COMBINED_COLORS = {
    "PD — M": "crimson",
    "PD — F": "salmon",
    "Control — M": "royalblue",
    "Control — F": "skyblue",
    "Invalid": "gray"
}

#---SELEZIONE TASK e METRICHE---
selected_task = st.sidebar.selectbox("Seleziona Task:", 
                             ("Task 1: 10 secondi in piedi con gli occhi aperti e i piedi alla larghezza delle spalle", 
                              "Task 2: 10 secondi in piedi con gli occhi chiusi e i piedi alla larghezza delle spalle",
                              "Task 3: 10 secondi in piedi con gli occhi aperti e i piedi uniti",
                              "Task 4: 10 secondi in piedi con gli occhi chiusi e i piedi uniti",
                              "Task 5: 10 secondi in piedi con gli occhi aperti e il piede destro al contatto con il tallone del piede sinistro",
                              "Task 6: 10 secondi in piedi con gli occhi aperti e il piede sinistro al contatto con il tallone del piede destro"
                              ), 
                              index=0
                              )

Scelta = {"Task 1: 10 secondi in piedi con gli occhi aperti e i piedi alla larghezza delle spalle": "T1_eyes_open_feet_shoulder", 
          "Task 2: 10 secondi in piedi con gli occhi chiusi e i piedi alla larghezza delle spalle": "T2_eyes_close_feet_shoulder",
          "Task 3: 10 secondi in piedi con gli occhi aperti e i piedi uniti": "T3_eyes_open_feet_together",
          "Task 4: 10 secondi in piedi con gli occhi chiusi e i piedi uniti": "T4_eyes_close_feet_together",
          "Task 5: 10 secondi in piedi con gli occhi aperti e il piede destro al contatto con il tallone del piede sinistro": "T5_eyes_open_Rfoot_forward",
          "Task 6: 10 secondi in piedi con gli occhi aperti e il piede sinistro al contatto con il tallone del piede destro": "T6_eyes_open_Lfoot_forward"
          }
df_final = pd.read_csv(fr"dataset\{Scelta[selected_task]}.csv")
#-----------------
df_final["Height (cm)"] = df_final["Height (cm)"]/100 
df_final = df_final.rename(columns={"Height (cm)": "Height (m)"}) 

D_demografiche = {
        "Maschio": "Male",
        "Femmina": "Female",
        "Età (anni)": "Age",
        "Altezza (m)": "Height (m)",
        "Peso (kg)": "Weight (kg)"
    }

#------------------
solette = st.sidebar.selectbox(
    "Metriche COP solette:",
    ["Sway path (cm)", "Velocità media (cm/s)", "Sway ML (cm)", "Sway AP (cm)","Area Ellisse 95% (cm²)"],
    )
globale = st.sidebar.selectbox(
    "Metriche COP pedana:",
    ["Sway path (cm)", "Velocità media (cm/s)", "Sway ML (cm)", "Sway AP (cm)", "Area Ellisse 95% (cm²)"],
    )

D_solette = {
    "Sway path (cm)": "path",
    "Velocità media (cm/s)": "vel",
    "Area Ellisse 95% (cm²)": "area",
    "Sway ML (cm)": "std_x",
    "Sway AP (cm)": "std_y",          
}

D_globale = {
    "Sway path (cm)": "global_path",
    "Sway ML (cm)": "sway_ml",
    "Sway AP (cm)": "sway_ap",
    "Velocità media (cm/s)": "velocity",
    "Area Ellisse 95% (cm²)": "Area"
}

#---TITOLO---

st.title("Balance Test" , anchor= False , text_alignment= "center")
st.write("Il partecipante si posizionava vicino al punto medio del tappetino sul lato. Per ogni sottocompito, al partecipante veniva chiesto di salire sul tappetino e iniziare il sottocompito di equilibrio, per poi scendere dal tappetino. Questo ha contribuito a segmentare i dati in base al sottocompito di equilibrio.")
st.markdown("<hr style='border-top:3px solid orange;margin-top:-5px;'>", unsafe_allow_html=True)
st.subheader(f"{selected_task}")

#---FILTRAGGIO DATI---

st.sidebar.subheader("Filtraggio dati:")

def filter_data(df_f, group, sex, age_range):
    if group != "Entrambi":
        df_f = df_f[df_f["Group"] == group]
    if sex != "Entrambi":
        df_f = df_f[df_f["Sex"] == sex]
    df_f = df_f[df_f["Age"].between(age_range[0], age_range[1])]
    return df_f  
 
with st.sidebar.expander("Filtri", expanded=False):

    group =st.radio("Gruppo:", ("PD","Control", "Entrambi"), index=2)

    sex = st.radio("Sesso:", ("Maschio", "Femmina", "Entrambi"), index=2)
    sex = D_demografiche[sex] if sex != "Entrambi" else "Entrambi"

    

    age_range = st.slider("Età (anni):", int(df_final["Age"].min()), int(df_final["Age"].max()), value=(int(df_final["Age"].min()), int(df_final["Age"].max())), step=5)


    filtered_df = filter_data(df_final, group, sex, age_range)

    number = st.number_input("Numero soggetti per gruppo (opzionale):", help="Seleziona un egual numero di soggetti per ciascun gruppo, scegliendo i soggetti più vicini alla media dell'età del campione filtrato.",
                min_value=1, 
                max_value=np.min([len(filtered_df[(filtered_df["Group"] == "Control") & (filtered_df["Invalid"] == False)]), len(filtered_df[(filtered_df["Group"] == "PD") & (filtered_df["Invalid"] == False)])]), 
                value=None 
                )  

def choose_samples(df, n, age_range):
    target_age = sum(age_range) / 2
        

    df = df[~df["Invalid"].fillna(False)] 
    def select_group(group_df):
        distances = (
            abs(group_df["Age"] - target_age))
        

        return group_df.loc[distances.nsmallest(min(n, len(group_df))).index] 

    control = select_group(df[df["Group"] == "Control"])
    pd_group = select_group(df[df["Group"] == "PD"])

    return pd.concat([control, pd_group]) 

if number:
    filtered_df = choose_samples(filtered_df, int(number), age_range) 
n_samples = [len(filtered_df), 
             ((filtered_df["Group"] == "PD")&(filtered_df["Sex"] == "Male")&(~filtered_df["Invalid"])).sum(), 
             ((filtered_df["Group"] == "PD")&(filtered_df["Sex"] == "Female")&(~filtered_df["Invalid"])).sum(),
             ((filtered_df["Group"] == "Control")&(filtered_df["Sex"] == "Male")&(~filtered_df["Invalid"])).sum(), 
             ((filtered_df["Group"] == "Control")&(filtered_df["Sex"] == "Female")&(~filtered_df["Invalid"])).sum(),
             filtered_df["Invalid"].sum(),
             len(df_final) - len(filtered_df)
            ]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Campioni ottenuti:", n_samples[0], border=True)
with col2:
    if group != "Control":
        st.metric("Campioni PD:", n_samples[1]+n_samples[2], border=True)
    else:        
        st.metric("Campioni PD:", "-", border=True)
with col3:
    if group != "PD":
        st.metric("Campioni Control:", n_samples[3]+n_samples[4], border=True)
    else:
        st.metric("Campioni Control:", "-", border=True)
with col4:
    st.metric("Campioni non validi:", n_samples[5], border=True , help="Campioni che hanno eseguito il test, ma presentano dati del centro di pressione insufficienti o errati per l'analisi.")

st.info(f"Sono stati filtrati {n_samples[6]} campioni", width="stretch")
filtered_df= filtered_df[~filtered_df["Invalid"].fillna(False)] 

def plot_pie_chart(pd_count_M, pd_count_F, control_count_M, control_count_F, invalid_count):
    labels = ["Control — M","Control — F", "PD — M", "PD — F", "Invalid"]
    values = [control_count_M, control_count_F, pd_count_M, pd_count_F, invalid_count]
    df_pie = pd.DataFrame({
        "Categoria": labels,
        "N": values
    })
    fig = px.pie(
        df_pie,
        names="Categoria",
        values="N",
        color="Categoria",
        color_discrete_map=COMBINED_COLORS,
        title=f"Composizione campione (n={n_samples[0]})",
        hole=0.35  
    )
    fig.update_traces(
        texttemplate="%{label}<br>%{percent}",
    )

    fig.update_layout(
        legend=dict( 
            
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig)

def age_histogram_plot(feature):
    fig = px.histogram(
        filtered_df,
        x=feature,
        category_orders={"Group": ["PD", "Control"]},
        color="Group",
        title="Distribuzione età per gruppo",
        color_discrete_map=COLOR_MAP,
        range_x=[filtered_df[feature].min(), filtered_df[feature].max()],
        labels={feature: "Età (anni)"},
        nbins=20,
        
    )

    fig.update_layout(template="simple_white", yaxis=dict(showgrid=True), height=400, barmode="group" , legend_title=None)
    st.plotly_chart(fig)

if n_samples[0] > 0:
    col1, col2 = st.columns(2)

    with col1:
        plot_pie_chart(n_samples[1], n_samples[2], n_samples[3], n_samples[4], n_samples[5])

    with col2:
        age_histogram_plot("Age")

#GRAFICI

def box_plot(feature, title, points_option):
    point = "all" if points_option else False
    fig = px.box(
        filtered_df,
        x="Group",
        category_orders={"Group": ["PD", "Control"]},
        y=feature,
        color="Group",
        color_discrete_map=COLOR_MAP, 
        points = point, 
        title=f"{title}",
        custom_data=["Subject ID", "Group", feature], 
        labels={feature: title}
    )
    fig.update_layout(
    xaxis_title=None,
    legend_title=None,
    )
    fig.update_traces(
        hovertemplate=
        "Subject ID: %{customdata[0]}<br>" +
        "Group: %{customdata[1]}<br>" +
        f"{feature}: %{{customdata[2]}}<extra></extra>"
    ) 

    event = st.plotly_chart(
        fig,
        width='stretch',
        on_select="rerun",
        selection_mode="points"
    ) 

    # gestione click
    if event and event.selection and event.selection["points"]:
        selected = event.selection["points"][0]["customdata"][0]

        st.session_state["selected_patient"] = selected

        st.switch_page("pages/3_Balance_Analysis_Single.py")

    return fig

def show_box_metrics(filtered_df, feature):
    group_order = ["PD", "Control"]
    metrics_list = []
    for group in group_order:
        
        col = filtered_df[(filtered_df["Group"] == group)][feature]
        if len(col) != 0:
            mean = col.mean()
            median = col.median()
            q1 = col.quantile(0.25)
            q3 = col.quantile(0.75)
            iqr = q3 - q1
            std = col.std()
            n_outliers = len(col[(col < q1 - 1.5*iqr) | (col > q3 + 1.5*iqr)])

            # Tabella metriche
            metrics_list.append({
                "Gruppo": group,
                #"N Persone": n_people,
                "Mediana": round(median, 2),
                "Media": round(mean, 2),
                "Deviazione Std": round(std, 2),
                "IQR": round(iqr, 2),
                "Outliers": n_outliers
            })

    # Visualizzazione tabella
    metrics_df = pd.DataFrame(metrics_list)
    st.dataframe(metrics_df, width='stretch', hide_index=True, 
                            column_config={
                            "IQR": st.column_config.NumberColumn(
                                "IQR",
                                help=(
                                    "Interquartile Range (Q3 - Q1).\n\n"
                                    "Misura la dispersione del 50% centrale dei dati."
                                ),
                                format="%.2f"
                            )
    })

def histogram_plot(feature, label_x):

    fig = px.histogram(
        filtered_df,
        x=feature,
        category_orders={"Group": ["PD", "Control"]},
        color="Group",
        title=f"Distribuzione {label_x} per gruppo",
        color_discrete_map=COLOR_MAP,
        range_x=[filtered_df[feature].min(), filtered_df[feature].max()],
        labels={feature: label_x, "count": "Frequenza"},
        nbins=25,
        
    )

    fig.update_layout(template="simple_white",yaxis=dict(showgrid=True), barmode="group" , legend_title=None)
    st.plotly_chart(fig)

def scatter_plot(X, Y, label_x, label_y, title):
    fig = px.scatter(
        filtered_df,
        x=f"{X}",   
        y=f"{Y}",
        color="Group",
        color_discrete_map=COLOR_MAP,
        category_orders={"Group": ["PD", "Control"]},
        trendline="ols",
        title=f"Scatter Plot of {title}",
        labels={f"{X}": label_x, f"{Y}": label_y},
        custom_data=["Subject ID", "Group", X]
    )
    fig.update_layout(
    legend_title=None, template="simple_white", yaxis=dict(showgrid=True),
    )
    fig.update_traces(
        hovertemplate=
        "Subject ID: %{customdata[0]}<br>" +
        "Group: %{customdata[1]}<br>" +
        f"{X}: %{{customdata[2]}}<extra></extra>"
    ) 

    event = st.plotly_chart(
        fig,
        width='stretch',
        on_select="rerun",
        selection_mode="points"
    ) 

    # gestione click
    if event and event.selection and event.selection["points"]:
        selected = event.selection["points"][0]["customdata"][0]

        st.session_state["selected_patient"] = selected

        #st.success(f"Paziente selezionato: {selected}")

        # opzionale: navigazione pagina paziente
        st.switch_page("pages/3_Balance_Analysis_Single.py")
    return fig

def show_scatter_metrcs(filtered_df, demo_var, scatter_metric):
    group_order = ["PD", "Control"]
    metrics_list = []
    for group in group_order:
        col = filtered_df[filtered_df["Group"] == group][[demo_var, scatter_metric]]
        n = len(col)
        if n < 3:
            continue

        rho, p_rho = spearmanr(col[demo_var], col[scatter_metric], nan_policy="omit")
        X = sm.add_constant(col[demo_var])
        ols = sm.OLS(col[scatter_metric], X).fit()

        metrics_list.append({
            "Gruppo": group,
            "Spearman ρ": round(rho, 3),
            "p Spearman": round(p_rho, 4),
            "Pendenza OLS": round(ols.params.iloc[1], 4)
        })
    return pd.DataFrame(metrics_list)
#SEZIONE BOX PLOT

with st.expander("BOX PLOT metriche solette: piede Destro e piede Sinistro"):
    st.header("Box plot " f"{solette}"" solette")    
    if solette == "Asimmetria (%)":
        if len(filtered_df[f"{D_solette[solette]}"]) == 0 or len(filtered_df[f"{D_solette[solette]}"]) == 0:
            st.error(f"Non risultano pazienti validi per la visualizzazione della metrica \"{solette}\", prova a modificare la sezione: Filtraggio dati")     
        else:
            st.caption("Mostra la distribuzione dei valori di asimmetria tra piede Destro e Sinistro per PD e Control: box = mediana e quartili, punti = singoli soggetti.")
            st.caption("Valori positivi indicano una maggiore instabilità, mentre valori intorno a zero indicano una simmetria tra i piedi.")
            points_option_1 = st.toggle("Mostra tutti i punti", value=True, key="points_toggle_1")
            box_plot(f"{D_solette[solette]}", f"Asimmetria (%) tra piede Destro e Sinistro", points_option_1)
            show_box_metrics(filtered_df, f"{D_solette[solette]}")
    else:
        if len(filtered_df[f"R_{D_solette[solette]}"]) == 0 or len(filtered_df[f"L_{D_solette[solette]}"]) == 0:
            st.error(f"Non risultano pazienti validi per la visualizzazione della metrica \"{solette}\", prova a modificare la sezione: Filtraggio dati")     
        else:
            st.caption("Mostra la distribuzione dei valori per PD e Control: box = mediana e quartili, punti = singoli soggetti.")
            points_option_2 = st.toggle("Mostra tutti i punti", value=True, key="points_toggle_2")
            col1, col2 = st.columns(2)
            with col1:
                box_plot(f"R_{D_solette[solette]}", f"{solette} piede Destro", points_option_2)
                show_box_metrics(filtered_df, f"R_{D_solette[solette]}") 
                
            with col2:
                box_plot(f"L_{D_solette[solette]}", f"{solette} piede Sinistro", points_option_2)
                show_box_metrics(filtered_df, f"L_{D_solette[solette]}")

with st.expander("BOX PLOT metriche pedana"):
    st.header("Box plot " f"{globale}"" pedana") 
    if len(filtered_df[f"{D_globale[globale]}"]) == 0:
        st.error(f"Non risultano pazienti validi per la visualizzazione della metrica \"{globale}\", prova a modificare la sezione: Filtraggio dati")
        
    else:
        st.caption("Mostra la distribuzione dei valori per PD e Control: box = mediana e quartili, punti = singoli soggetti.")
        points_option_3 = st.toggle("Mostra tutti i punti", value=True, key="points_toggle_3")
        box_plot(f"{D_globale[globale]}", f"{globale}", points_option_3)
        show_box_metrics(filtered_df, f"{D_globale[globale]}")

with st.expander("ISTOGRAMMA metriche pedana"):
    st.header("Istogramma " f"{globale}"" pedana")
    if len(filtered_df[f"{D_globale[globale]}"]) == 0:
        st.error(f"Non risultano pazienti validi per la visualizzazione della metrica \"{globale}\", prova a modificare la sezione: Filtraggio dati")
    else:    
        st.caption("Frequenza dei valori della metrica per i due gruppi.")
        histogram_plot(f"{D_globale[globale]}", f"{globale}")

#SEZIONE TEST STATISTICO

with st.expander("Test statistico: PD vs Control"):
    st.header("Test statistico per " f"{globale}"" globale")
    st.caption(
        "Shapiro-Wilk verifica la normalità; in base al risultato viene consigliato t-test di Welch o Mann-Whitney U."
    )

    control = filtered_df[filtered_df["Group"] == "Control"][f"{D_globale[globale]}"].dropna()
    pd_group = filtered_df[filtered_df["Group"] == "PD"][f"{D_globale[globale]}"].dropna()

    def detect_outliers(series):
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        return ((series < lower) | (series > upper)).sum()
    
    if len(pd_group) > 1 and len(control) > 1:

        sw_info = {} 
        all_normal = True

        for g, name in [(pd_group, "PD"), (control, "Control")]: 
            if len(g) < 3:
                sw_info[name] = None
                all_normal = False
            else:
                _, p_sw = shapiro(g.sample(min(len(g), 1000), random_state=42)) 
                sw_info[name] = p_sw 
                if p_sw < 0.05:
                    all_normal = False
    #parte relativa alla presenza o meno di outlier che posso influenzare il mio test
        n_out_control = detect_outliers(control) #
        n_out_pd = detect_outliers(pd_group)

        outlier_present = (n_out_control > 0 or n_out_pd > 0)

        # =========================
        # SHAPIRO DISPLAY
        # =========================

        sw_col1, sw_col2 = st.columns(2)

        for col, (name, p_sw) in zip([sw_col1, sw_col2], sw_info.items()): #
            with col:
                if p_sw is None:
                    st.metric(f"Shapiro-Wilk {name}", "—", help="n < 3")
                else:
                    normal = p_sw >= 0.05
                    st.metric(
                        f"Shapiro-Wilk {name}",
                        f"p = {p_sw:.4f}",
                        delta="Normale" if normal else "Non normale",
                        delta_color="normal" if normal else "inverse",
                    )

        # =========================
        # CONSIGLIO TEST
        # =========================

        if all_normal and not outlier_present:
            st.success("Entrambi i gruppi sono normali e senza outlier → consigliato Welch's t-test")
        else:
            st.warning("Non normalità o outlier presenti → consigliato Mann–Whitney U test")

        # =========================
        # BOTTONI
        # =========================
        if all_normal and not outlier_present:
            test = st.segmented_control ("**Test:**", ["Welch's T-test", "Mann-Whitney U test"], default="Welch's T-test", width="stretch")
        else:
            test = st.segmented_control("**Test:**", ["Welch's T-test", "Mann-Whitney U test"], default="Mann-Whitney U test", width="stretch") 

        # =========================
        # TEST STATISTICI (logica tua originale)
        # =========================

        t_stat, t_p = ttest_ind(control, pd_group, nan_policy='omit', equal_var=False)
        w_stat, w_p = mannwhitneyu(control, pd_group, alternative="two-sided")

        if test == "Welch's T-test":
            r1, r2, r3 = st.columns(3)

            r1.metric("t-statistic", f"{t_stat:.4f}")
            r2.metric("p-value", f"{t_p:.6f}")

            with r3:
                if t_p < 0.05:
                    st.success("Significativo (p < 0.05)")
                else:
                    st.info("Non significativo")

        if test == "Mann-Whitney U test":
            r1, r2, r3 = st.columns(3)

            r1.metric("U-statistic", f"{w_stat:.4f}")
            r2.metric("p-value", f"{w_p:.6f}")

            with r3:
                if w_p < 0.05:
                    st.success("Significativo (p < 0.05)")
                else:
                    st.info("Non significativo")

    else:
        st.warning(
            f"Campioni insufficienti per \"{globale}\", prova a modificare la sezione: Filtraggio dati"
        )

#---SCATTER PLOT---

with st.expander("SCATTER PLOT"):
    st.header("Scatter Plot: Metrica pedana vs Demografici")

    col1, col2 = st.columns(2)
    with col1:
        y_metriche = st.selectbox(
            "Scegli la metrica COP globale asse Y:",
            ["Sway path (cm)", "Velocità media (cm/s)", "Area Ellisse 95% (cm²)", "Sway ML (cm)", "Sway AP (cm)"]
        )
    with col2:
        x_demo = st.selectbox(
            "Scegli demografica asse X:", 
            ["Età (anni)", "Altezza (m)", "Peso (kg)"]
        )

    if len(filtered_df[D_globale[y_metriche]]) == 0 or len(filtered_df[D_demografiche[x_demo]]) == 0:
        st.error(f"Non risultano pazienti validi per la visualizzazione della metrica \"{y_metriche}\", prova a modificare la sezione: Filtraggio dati")
            
    else:
        scatter_plot(D_demografiche[x_demo], D_globale[y_metriche] , x_demo, y_metriche,  f"{y_metriche} vs {x_demo}")
        st.dataframe(show_scatter_metrcs(filtered_df, D_demografiche[x_demo], D_globale[y_metriche]), width="stretch", hide_index=True)