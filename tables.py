import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="shortline.proxy.rlwy.net",
        port=49015,
        user="root",
        password="FMIbNxZfbWGVexqtTNKaJzbOTcxvmoPP",
        database="railway"
    )

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS beneficiaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    zone VARCHAR(50)
)
""")

cursor.execute("""
INSERT IGNORE INTO users (username, password, full_name)
VALUES ('bams', 'bamud2003', 'bamud')
""")

conn.commit()
cursor.close()
conn.close()

print("Tables créées avec succès ✅")
