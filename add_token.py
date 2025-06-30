import sqlite3

conn = sqlite3.connect("epic_crm.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE user ADD COLUMN token TEXT")
    conn.commit()
    print("✅ Colonne 'token' ajoutée à la table user.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️ La colonne 'token' existe déjà.")
    else:
        print(f"❌ Erreur : {e}")
finally:
    conn.close()
