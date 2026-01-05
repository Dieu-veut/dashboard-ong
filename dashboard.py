import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# --- Connexion à la base Railway ---
def get_connection():
    return mysql.connector.connect(
        host="shortline.proxy.rlwy.net",   # ton host public Railway
        port=49015,                        # ton port Railway
        user="root",                        # ton user Railway
        password="FMIbNxZfbWGVexqtTNKaJzbOTcxvmoPP",  # ton password
        database="railway"                 # nom de ta base
    )

# --- Login page ---
st.title("Dashboard ONG")

username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        st.success(f"Bienvenue {user[3]} !")  # full_name
        st.session_state['logged_in'] = True
    else:
        st.error("Nom d'utilisateur ou mot de passe incorrect")

# --- Dashboard page ---
if st.session_state.get('logged_in'):

    st.subheader("Ajouter des bénéficiaires depuis CSV")
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Insérer les données dans MySQL
        conn = get_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute(
                "INSERT INTO beneficiaries (name, age, zone) VALUES (%s, %s, %s)",
                (row['name'], row['age'], row['zone'])
            )
        conn.commit()
        cursor.close()
        conn.close()

        st.success("Données insérées avec succès !")
        st.dataframe(df)

    # --- Graphiques ---
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM beneficiaries", conn)
    conn.close()

    if not df.empty:
        st.subheader("Nombre de bénéficiaires par zone")
        fig = px.bar(df.groupby("zone").size().reset_index(name="count"), x="zone", y="count")
        st.plotly_chart(fig)

        st.subheader("Liste complète des bénéficiaires")
        st.dataframe(df)

