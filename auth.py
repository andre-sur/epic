import sqlite3
import getpass
import bcrypt
import os
import json

DB_PATH = 'epic_crm.db'
_current_user = None
SESSION_FILE = ".session"

def connecter_utilisateur():
    global _current_user
    if _current_user:
        print(f"🔐 Utilisateur déjà connecté : {_current_user['name']} ({_current_user['role']})")
        return _current_user

    print("Afin de commencer votre session, entrez Email et Mot de passe.")
    email = input("Email : ").strip()
    if not email:
        print("❌ L'email ne peut pas être vide.")
        return None

    password = getpass.getpass("Mot de passe : ").encode('utf-8')
    if not password:
        print("❌ Le mot de passe ne peut pas être vide.")
        return None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password, role FROM user WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        user_id, name, email, hashed_password, role = row
        if bcrypt.checkpw(password, hashed_password.encode('utf-8')):
            print(f"✅ Connecté avec succès – {name} ({role})")
            _current_user = {'id': user_id, 'name': name, 'email': email, 'role': role}
            save_user_session(_current_user)
            return _current_user
        else:
            print("❌ Mot de passe incorrect.")
    else:
        print("❌ Utilisateur non trouvé.")
    return None


def deconnecter_utilisateur():
    global _current_user
    if not _current_user:
        print("ℹ️ Aucun utilisateur connecté.")
        return
    print(f"🔓 Déconnexion de {_current_user['name']}.")
    _current_user = None

def get_cached_user():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def save_user_session(utilisateur):
    with open(SESSION_FILE, "w") as f:
        json.dump(utilisateur, f)