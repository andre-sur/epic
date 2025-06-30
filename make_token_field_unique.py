import sqlite3

conn = sqlite3.connect('epic_crm.db')
cursor = conn.cursor()

# Crée un index unique sur la colonne token
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_token_unique ON user(token);")

conn.commit()
conn.close()
print("✅ L'index unique sur 'token' a été ajouté.")
