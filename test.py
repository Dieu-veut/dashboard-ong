import mysql.connector

# Connexion à MariaDB
conn = mysql.connector.connect(
    host="localhost",
    user="bams",          # ton utilisateur
    password="bamud2003",   # ton mot de passe
    database="my_first"
)

cursor = conn.cursor()

# Lire les données
cursor.execute("SELECT * FROM beneficiaries")

for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT zone, COUNT(*) FROM beneficiaries GROUP BY zone")
for zone, total in cursor.fetchall():
    print(f"{zone}: {total} bénéficiaires")

cursor.close()
conn.close()



