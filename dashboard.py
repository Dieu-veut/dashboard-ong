import streamlit as st
import pandas as pd
import mysql.connector
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
def get_connection():
    return mysql.connector.connect(
        host="shortline.proxy.rlwy.net",
        port=49015,
        user="root",
        password="FMIbNxZfbWGVexqtTNKaJzbOTcxvmoPP",
        database="railway"
    )

# ===============================
# PAGE LOGIN
# ===============================
if not st.session_state.logged_in:
    st.title("🔐 Connexion Dashboard ONG")

    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
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
            st.rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")

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
    if uploaded_file.name.endswith(".csv"):
        df_new = pd.read_csv(uploaded_file)
    else:
        df_new = pd.read_excel(uploaded_file)

    st.success("Fichier chargé avec succès")
    st.dataframe(df_new)

    # Connexion DB
    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df_new.iterrows():
        cursor.execute(
            """
            INSERT INTO beneficiaries (name, age, zone)
            VALUES (%s, %s, %s)
            """,
            (row["name"], int(row["age"]), row["zone"])
        )

    conn.commit()
    cursor.close()
    conn.close()

    st.success("✅ Données enregistrées dans la base")

# ===============================
# LECTURE DES DONNÉES
# ===============================
conn = get_connection()
df = pd.read_sql("SELECT * FROM beneficiaries", conn)
conn.close()

if df.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

df["age"] = pd.to_numeric(df["age"], errors="coerce")
df = df.dropna(subset=["age"])

# ===============================
# FILTRES
# ===============================
st.header("🎯 Filtres")

zones = df["zone"].unique().tolist()
selected_zone = st.selectbox("Zone", ["Toutes"] + zones)

min_age = int(df["age"].min())
max_age = int(df["age"].max())

selected_age = st.slider(
    "Âge",
    min_value=18,
    max_value=120,
    value=(min_age, max_age)
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
df_grouped = df.groupby("zone").size().reset_index(name="total")

fig = px.bar(
    df_grouped,
    x="zone",
    y="total",
    title="Nombre de bénéficiaires par zone"
)

st.plotly_chart(fig, use_container_width=True)
