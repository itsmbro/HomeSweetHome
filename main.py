import streamlit as st
import json
import requests
import pandas as pd
import plotly.express as px

# Configura le variabili per GitHub
GITHUB_REPO = "nome-utente/nome-repo"
GITHUB_FILE_PATH = "data.json"
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# Funzione per caricare il JSON da GitHub
def load_data():
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE_PATH}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

# Funzione per salvare il JSON su GitHub
def save_data(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None
    
    new_data = json.dumps(data, indent=4)
    payload = {
        "message": "Aggiornamento dati",
        "content": new_data.encode("utf-8").decode("latin1"),
        "sha": sha
    }
    requests.put(url, headers=headers, json=payload)

# Carica i dati iniziali
data = load_data()

st.title("💰 Budget Tracker")

# Input per nuova voce
new_key = st.text_input("Nome della voce:")
new_value = st.number_input("Valore (€):", min_value=0.0, step=0.01)
if st.button("Aggiungi"):
    if new_key and new_value:
        data[new_key] = new_value
        save_data(data)
        st.rerun()


# Rimuovere voce
remove_key = st.selectbox("Seleziona una voce da rimuovere:", options=[""] + list(data.keys()))
if st.button("Rimuovi") and remove_key:
    del data[remove_key]
    save_data(data)
    st.rerun()


# Mostra le voci e i valori
if data:
    df = pd.DataFrame(list(data.items()), columns=["Voce", "Valore (€)"])
    st.write(df)
    
    # Grafico a torta
    fig = px.pie(df, names="Voce", values="Valore (€)", title="Distribuzione Spese")
    st.plotly_chart(fig)
else:
    st.write("Nessuna voce aggiunta.")
