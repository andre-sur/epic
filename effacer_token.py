import sqlite3

DB_PATH = 'epic_crm.db'
email = input("Email de l'utilisateur dont vous voulez supprimer le token : ").strip()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("UPDATE user SET token = NULL WHERE email = ?", (email,))
conn.commit()
conn.close()

print("✅ Token supprimé pour l'utilisateur :", email)
