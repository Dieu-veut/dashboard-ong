import pandas as pd
import mysql.connector

# Lire le CSV
df = pd.read_csv("users.csv")

# Normaliser les emails
df['email'] = df['email'].str.lower()

# Connexion à MariaDB
conn = mysql.connector.connect(
    host="localhost",
    user="bams",
    password="bamud2003",  # laisse vide si tu n'as pas défini de mot de passe
    database="my_first"
)
cursor = conn.cursor()

# # Insérer les données
# for _, row in df.iterrows():
#     cursor.execute(
#         "INSERT INTO users (name, email, country) VALUES (%s, %s, %s)",
#         (row['name'], row['email'], row['country'])
#     )

# conn.commit()
# cursor.close()
# conn.close()

print("Données insérées avec succès !")
