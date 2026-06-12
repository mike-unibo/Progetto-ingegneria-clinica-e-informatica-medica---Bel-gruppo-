import streamlit as st

st.set_page_config(page_title="WearGait-PD · Login")


st.title("🔐 Accesso WearGait-PD")

# Creazione di un dizionario Python chiamato UTENTI
# Ogni coppia "chiave : valore" rappresenta --> "username : password"
UTENTI = {
    "utente1": "password1",
    "utente2": "password2",
    "utente3": "password3",
}

# Crea un form chiamato "login_form". Tutti gli elementi inseriti dentro il blocco "with" faranno parte dello stesso modulo di login
with st.form("login_form"):
    # Crea una casella di testo per inserire lo username. Il testo "Username" sarà mostrato sopra/interno al campo
    username = st.text_input("Username")

    # Crea una casella di testo per la password, type="password" serve a nascondere i caratteri digitati sostituendoli con pallini o asterischi
    password = st.text_input("Password", type="password")

    # Crea un pulsante con scritto "Accedi". Quando l'utente lo preme: submitted diventa True, altrimenti resta False
    submitted = st.form_submit_button("Accedi")

# Controlla se il pulsante "Accedi" è stato premuto
if submitted:
    # Verifica se: esiste lo username nel dizionario UTENTI e la password inserita corrisponde a quella salvata
    
    # UTENTI.get(username) restituisce la password associata allo username inserito
    if UTENTI.get(username) == password:

        # Salva nella sessione il fatto che l'utente è autenticato e viene creata una variabile chiamata "logged_in" con valore True
        st.session_state.logged_in = True

        # Ricarica completamente l'app Streamlit (utile per aggiornare la pagina dopo il login)
        st.rerun()

    else:
        # Se username o password sono sbagliati, mostra un messaggio di errore rosso nella pagina
        st.error("Credenziali errate")