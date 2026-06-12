import streamlit as st
#  Configurazione della pagina: imposto titolo, icona e stato iniziale della sidebar
st.set_page_config(page_title="WearGait-PD · Home", page_icon="icon.png", layout="wide", initial_sidebar_state="collapsed")

#  Intestazione
st.title("WearGait-PD · Data Explorer")
st.caption(
    "Dataset open-access per lo studio del cammino nella malattia di Parkinson · "
    "185 partecipanti · Johns Hopkins / FDA / VA Seattle"
)
st.divider()

st.subheader("Seleziona un'area di analisi")
st.write("Clicca su una sezione per esplorare i dati corrispondenti.")

#  RIGA 1: contiene le cards per Demografici + Gait
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.header(":blue[Dati Demografici]", divider="blue")
        st.caption("OVERVIEW · MOCA · COMORBIDITÀ")
        st.write(
            "Metriche chiave del dataset. "
            "Distribuzione del campione per età, sesso e gruppo clinico. "
            "Score MoCA e indici UPDRS III. "
            "Confronto H&Y - con DBS vs senza DBS"
        )
        st.write("**Contenuto:** età · sesso · MoCA score · UPDRS III · H&Y score · DBS")
        st.divider()
        if st.button("Apri Dati Demografici →", width='stretch', key="btn_demo"):
            st.switch_page("pages/1_Dati_Demografici.py")

with col2:
    with st.container(border=True):
        st.header(":green[Gait Analysis]", divider="green")
        st.caption("CAMMINO · PARAMETRI SPAZIO-TEMPORALI· PMKAS WALKWAY")
        st.write("Parametri del cammino acquisiti con tappeto strumentato") 
        st.write("SelfPace e HurriedPace")
        st.write("**Contenuto:** step length · step time · stride width · velocità · cadenza")
        st.divider()
        
        if st.button("Apri Gait Analysis →",
                     width='stretch', key="btn_gait"):
            st.switch_page("pages/2_Gait_Analysis.py")
st.write("")

#  RIGA 2: contiene le cards per Balance + FHIR
col3, col4 = st.columns(2, gap="large")

with col3:
    with st.container(border=True):
        st.header(":orange[Balance Analysis]", divider="orange")
        st.caption("EQUILIBRIO · SOLETTE · 6 PROVE")
        st.write(
            "Heatmap della pressione plantare durante le 6 prove di "
            "equilibrio statico. Eyes open/closed, piedi uniti, "
            "piedi a spalla e tandem."
        )
        st.write("**Contenuto:** heatmap piede · 16 sensori · forza totale")
        st.divider()
        if st.button("Apri Group Analysis →", width='stretch', key="btn_balance_group"):
            st.switch_page("pages/3_Balance_Analysis_Group.py")
        if st.button("Apri Single Patient Analysis →", width='stretch', key="btn_balance_single"):
            st.switch_page("pages/3_Balance_Analysis_Single.py")

with col4:
    with st.container(border=True):
        st.header(":violet[Dati Avanzati · FHIR]", divider="violet")
        st.caption("STANDARD HL7 · INTEROPERABILITÀ")
        st.write(
            "Mapping delle variabili cliniche e biomeccaniche in formato HL7 FHIR. " \
            "Risorse Patient, Condition, Observation e Bundle per l'interoperabilità dei dati sanitari."
        )
        st.write("**Contenuto:** HL7 FHIR · Patient · Condition · Observation · Bundle")
        st.divider()
        if st.button("Apri Dati Avanzati →",
                     width='stretch', key="btn_fhir"):
            st.switch_page("pages/4_FHIR.py")
