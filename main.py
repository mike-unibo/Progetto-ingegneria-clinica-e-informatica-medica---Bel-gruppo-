import streamlit as st

# Definisce tutte le pagine dell'app come oggetti st.Page.
# Ogni pagina punta a un file Python e ha un titolo che appare nella sidebar.
# "default=True" indica la pagina mostrata di default quando Streamlit
# non sa quale pagina caricare (es. dopo un refresh).
# NB: default=True su "login" serve quando l'utente NON è loggato,
#     default=True su "home" serve quando l'utente È loggato.
login            = st.Page("login.py",                            title="Login",            default=True)
home             = st.Page("pages/0_Home.py",                     title="Home",             default=True)
demografici      = st.Page("pages/1_Dati_Demografici.py",         title="Dati Demografici"              )
gait             = st.Page("pages/2_Gait_Analysis.py",            title="Gait Analysis"                 )
balance_group    = st.Page("pages/3_Balance_Analysis_Group.py",   title="Balance - Group Analysis"      )
balance_single   = st.Page("pages/3_Balance_Analysis_Single.py",  title="Balance - Single Patient"      )
fhir             = st.Page("pages/4_FHIR.py",                     title="FHIR"                          )
codesystem       = st.Page("pages/codesystem.py",                 title="Codesystem", visibility="hidden")

# Controllo accesso: session_state persiste tra le riesecuzioni dello script.
# Se "logged_in" è True (impostato dal login.py dopo credenziali corrette)
# mostra tutte le pagine dell'app. Altrimenti mostra solo il login.
if st.session_state.get("logged_in"):
    pg = st.navigation([home, demografici, gait, balance_group, balance_single, fhir, codesystem])
else:
    pg = st.navigation([login])

# Esegue la pagina selezionata dall'utente nella sidebar.
# Questo è il punto in cui Streamlit carica e renderizza il contenuto.
pg.run()