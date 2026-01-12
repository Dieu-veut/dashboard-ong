import streamlit as st
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import plotly.express as px

# ===============================
# CONFIG STREAMLIT
# ===============================
st.set_page_config(page_title="Dashboard ONG", layout="wide")

# ===============================
# SESSION LOGIN
# ===============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# ===============================
# CONNEXION BASE DE DONNÉES (Railway MySQL)
# ===============================
DB_CONFIG = {
    "host": "shortline.proxy.rlwy.net",
    "port": 49015,
    "user": "root",
    "password": "FMIbNxZfbWGVexqtTNKaJzbOTcxvmoPP",
    "database": "railway"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Pour pandas.read_sql avec sqlalchemy
def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

# ===============================
# PAGE LOGIN
# ===============================
if not st.session_state.logged_in:
    st.title("🔐 Connexion Dashboard ONG")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
    st.session_state.logged_in = True
    st.session_state.user = user["username"]
    st.success("Connexion réussie ✅")
    # Recharge la page
    st.stop()

            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")
        except Exception as e:
            st.error(f"Erreur de connexion à la base : {e}")

    st.stop()

# ===============================
# DASHBOARD
# ===============================
st.title("📊 Dashboard ONG – Gestion des bénéficiaires")
st.write(f"Connecté en tant que : **{st.session_state.user}**")

# ===============================
# IMPORT CSV / EXCEL
# ===============================
st.header("📥 Importer des données")

uploaded_file = st.file_uploader(
    "Choisir un fichier CSV ou Excel",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df_new = pd.read_csv(uploaded_file)
        else:
            df_new = pd.read_excel(uploaded_file)

        # Nettoyage des données
        df_new = df_new.dropna(subset=["name", "age", "zone"])
        df_new["age"] = pd.to_numeric(df_new["age"], errors="coerce")
        df_new = df_new.dropna(subset=["age"])
        df_new["age"] = df_new["age"].astype(int)

        st.success("Fichier chargé et nettoyé ✅")
        st.dataframe(df_new)

        # Insertion en base
        conn = get_connection()
        cursor = conn.cursor()

        for _, row in df_new.iterrows():
            cursor.execute(
                """
                INSERT INTO beneficiaries (name, age, zone)
                VALUES (%s, %s, %s)
                """,
                (row["name"], row["age"], row["zone"])
            )

        conn.commit()
        cursor.close()
        conn.close()

        st.success("✅ Données enregistrées dans la base")

    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier : {e}")

# ===============================
# LECTURE DES DONNÉES
# ===============================
try:
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM beneficiaries", engine)
except Exception as e:
    st.error(f"Erreur lors de la lecture des données : {e}")
    st.stop()

if df.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df = df.dropna(subset=["age"])
df["age"] = df["age"].astype(int)

# ===============================
# FILTRES
# ===============================
st.header("🎯 Filtres")

zones = df["zone"].dropna().unique().tolist()
selected_zone = st.selectbox("Zone", ["Toutes"] + zones)

# Slider âge robuste
min_age = int(df["age"].min())
max_age = int(df["age"].max())

selected_age = st.slider(
    "Âge",
    min_value=18,
    max_value=120,
    value=(max(min_age, 18), min(max_age, 120))
)

df_filtered = df.copy()

if selected_zone != "Toutes":
    df_filtered = df_filtered[df_filtered["zone"] == selected_zone]

df_filtered = df_filtered[
    (df_filtered["age"] >= selected_age[0]) &
    (df_filtered["age"] <= selected_age[1])
]

# ===============================
# TABLEAU
# ===============================
st.subheader("📋 Liste des bénéficiaires")
st.dataframe(df_filtered)

# ===============================
# GRAPHIQUE
# ===============================
st.subheader("📊 Répartition par zone")
df_grouped = df_filtered.groupby("zone").size().reset_index(name="total")

fig = px.bar(
    df_grouped,
    x="zone",
    y="total",
    title="Nombre de bénéficiaires par zone"
)

st.plotly_chart(fig, use_container_width=True)
