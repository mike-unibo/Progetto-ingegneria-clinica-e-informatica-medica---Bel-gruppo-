import streamlit as st
import pandas as pd
import utilsm as u

st.set_page_config(page_title="WearGait-PD · Code System locale e Concept Map",  layout='wide', page_icon="icon.png")

st.session_state["generated"] = False
st.page_link(r"pages\4_FHIR.py", label="<- Torna a costruttore risorse FHIR ")
st.header('Dettaglio Code System biomeccanico', text_alignment="center", divider="violet")

cs = pd.read_excel(r"dataset\codesystem_biomech.xlsx", dtype={"target_code": str}, skiprows=range(1,6))
cs["target_code"].replace("nan", "")
with st.container():
    st.markdown('''Per mappare alcune variabili biomeccaniche complesse presenti o derivate dal dataset Weargait PD
                è stato definito un CodeSystem locale in quanto non sono stati individuati concetti sufficientemente
                specifici all'interno delle principali ontologie mediche (LOINC, SNOMED).  
                La struttura del CodeSystem è documentata in questa pagina. Sono disponibili anche le relative risorse FHIR CodeSystem e ConceptMap.''')
    st.table(data=cs, width="content", height="content")
    cs1 = cs.to_csv()
    st.download_button(label="Download descrizione codesystem", data=cs1, mime="text/csv", file_name="codesystem.csv", icon=":material/download:" )

with st.expander("Risorse CodeSystem e ConceptMap", expanded=False):
    format = st.selectbox('Inserisci il formato in cui ti servono le risorsa: ', ('.JSON','.XML'), index=0)
    tab1, tab2 = st.tabs(['Preview risorsa "CodeSystem"', 'Preview risorsa "ConceptMap"'])

    with tab1:
        r = u.serialize(u.create_fhir_codesystem(), format)
        st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
        if format==".XML":
            st.code(r,language=format.lower()[1:])  
        else:
            st.json(r)
        g = st.download_button(label='Scarica risorsa '+format, data=r, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name="CodeSystem_Weargait_PD"+format, icon=":material/download:", key=0)

    with tab2:
        r1 = u.serialize(u.create_fhir_conceptmap(), format)
        st.badge('Risorsa generata con successo', icon=':material/done_outline:', color='green')
        if format==".XML":
            st.code(r1,language=format.lower()[1:])  
        else:
            st.json(r1)
        g = st.download_button(label='Scarica risorsa '+format, data=r1, mime='text/'+ (format[1:] if format=='.XML' else 'javascript'), file_name="ConceptMap_Weargait_PD"+format, icon=":material/download:", key=1)

st.page_link(r"pages\4_FHIR.py", label="<- Torna a costruttore risorse FHIR ")