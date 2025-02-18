import streamlit as st
import json
import requests
import base64
import plotly.express as px

# Configurazione GitHub
GITHUB_USER = "itsmbro"
GITHUB_REPO = "HomeSweetHome"
GITHUB_BRANCH = "main"
GITHUB_FILE_PATH = "dati.json"

def load_budget_data():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FILE_PATH}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        budget_data = {}
        save_budget_data(budget_data)
        return budget_data

def save_budget_data(budget_data):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    json_data = json.dumps(budget_data, ensure_ascii=False, indent=4)
    json_base64 = base64.b64encode(json_data.encode()).decode()

    data = {
        "message": "Aggiornamento budget_data.json",
        "content": json_base64,
        "branch": GITHUB_BRANCH
    }
    
    if sha:
        data["sha"] = sha  

    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        st.error(f"Errore aggiornamento GitHub: {response.json()}")

# Carica il budget dal file JSON
budget_data = load_budget_data()

st.title("💰 Gestione Budget")

# Input per aggiungere nuove voci
col1, col2 = st.columns(2)
with col1:
    new_key = st.text_input("Nome voce di spesa")
with col2:
    new_value = st.number_input("Importo (€)", min_value=0.0, format="%.2f")

if st.button("Aggiungi/Modifica voce"):
    if new_key and new_value:
        budget_data[new_key] = new_value
        save_budget_data(budget_data)
        st.rerun()
    else:
        st.warning("Inserisci sia il nome della voce che l'importo!")

# Rimuovere una voce
remove_key = st.selectbox("Seleziona una voce da rimuovere", list(budget_data.keys()), index=0) if budget_data else None
if remove_key and st.button("Rimuovi voce"):
    del budget_data[remove_key]
    save_budget_data(budget_data)
    st.rerun()

# Mostra il budget aggiornato
data_items = list(budget_data.items())
if data_items:
    df = {"Voce": [x[0] for x in data_items], "Importo (€)": [x[1] for x in data_items]}
    st.table(df)

    # Grafico a torta
    fig = px.pie(values=df["Importo (€)"], names=df["Voce"], title="Distribuzione Spese")
    st.plotly_chart(fig)
else:
    st.info("Nessuna voce di spesa presente.")
