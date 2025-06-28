import sqlite3
import getpass
import bcrypt  # à installer avec pip install bcrypt

DB_PATH = 'epic_crm.db'

def connecter_utilisateur():
    email = input("Email : ").strip()
    password = getpass.getpass("Mot de passe : ").encode('utf-8')  # invisible

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, password, role FROM user WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row:
        user_id, name, email, hashed_password, role = row
        if bcrypt.checkpw(password, hashed_password.encode('utf-8')):
            print(f"\n✅ Bienvenue {name} ({role})")
            return {
                'id': user_id,
                'name': name,
                'email': email,
                'role': role
            }
        else:
            print("⛔️ Mot de passe incorrect.")
    else:
        print("⛔️ Utilisateur non trouvé.")

    return None
