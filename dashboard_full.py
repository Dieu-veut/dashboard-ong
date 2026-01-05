import streamlit as st
import mysql.connector
import pandas as pd

# ======================
# INIT SESSION
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ======================
# FONCTION DB
# ======================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="bams",
        password="bamud2003",
        database="my_first"
    )


if not st.session_state.logged_in:
    st.title("🔐 Connexion Dashboard ONG")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM user WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            st.session_state.logged_in = True
            st.session_state.user = user["username"]
            st.success("Connexion réussie ✅")
            st.rerun()   # 🔥 IMPORTANT
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

    st.stop()   # 🔥 BLOQUE LE DASHBOARD



st.set_page_config(page_title="Dashboard ONG", layout="wide")
st.title("Dashboard ONG - Bénéficiaires")

# ----- SECTION 1 : Import CSV -----
st.header("Importer de nouvelles données")

uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")

if uploaded_file is not None:
    df_new = pd.read_csv(uploaded_file)
    
    # Connexion MariaDB
    conn = mysql.connector.connect(
        host="localhost",
        user="bams",
        password="bamud2003",
        database="my_first"
    )
    cursor = conn.cursor()
    
    # Insérer chaque ligne
    for _, row in df_new.iterrows():
        cursor.execute(
            "INSERT INTO beneficiaries (name, age, zone) VALUES (%s, %s, %s)",
            (row['name'], row['age'], row['zone'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    st.success("Les données ont été importées avec succès !")

# ----- SECTION 2 : Récupérer toutes les données -----
conn = mysql.connector.connect(
    host="localhost",
    user="bams",
    password="bamud2003",
    database="my_first"
)
df = pd.read_sql("SELECT * FROM beneficiaries", conn)
conn.close()

# ----- SECTION 3 : Filtres -----
st.header("Filtres des bénéficiaires")
zones = df['zone'].unique().tolist()
selected_zone = st.selectbox("Filtrer par zone :", ["Toutes"] + zones)

min_age, max_age = int(df['age'].min()), int(df['age'].max())
selected_age = st.slider("Filtrer par âge :", min_age, max_age, (min_age, max_age))

df_filtered = df.copy()

if selected_zone != "Toutes":
    df_filtered = df_filtered[df_filtered['zone'] == selected_zone]

df_filtered = df_filtered[(df_filtered['age'] >= selected_age[0]) & (df_filtered['age'] <= selected_age[1])]

# ----- SECTION 4 : Tableau et Graphiques -----
st.subheader("Tableau des bénéficiaires")
st.dataframe(df_filtered)

st.subheader("Graphique des bénéficiaires par zone")
df_grouped = df.groupby('zone').size().reset_index(name='total')
st.bar_chart(df_grouped.set_index('zone'))
