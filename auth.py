import sqlite3
import getpass
import bcrypt
import os
import json
import jwt
from datetime import datetime, timedelta

DB_PATH = 'epic_crm.db'
SESSION_FILE = ".session"
SECRET_KEY = "supersecretkey"
TOKEN_EXP_MINUTES = 3
_current_user = None


def make_token(user_id):
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_EXP_MINUTES)
    payload = {"user_id": user_id, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def is_token_valid(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        print("⏰ Le token a expiré.")
        return False
    except jwt.InvalidTokenError:
        print("Erreur- Token invalide.")
        return False


def login():
    global _current_user
    if _current_user:
        print(f" Déjà connecté : {_current_user['name']} ({_current_user['role']})")
        return _current_user

    print("CONNEXION DE L'UTILISATEUR")
    print("==========================")
    email = input("Email : ").strip()
    if not email:
        print(" L'email est requis.")
        return None

    password = getpass.getpass("Mot de passe : ").encode('utf-8')
    if not password:
        print(" Le mot de passe est requis.")
        return None

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password, role FROM user WHERE email = ?", (email,))
    row = cursor.fetchone()

    if row:
        user_id, name, email, hashed_pw, role = row
        if bcrypt.checkpw(password, hashed_pw.encode('utf-8')):
            token = make_token(user_id)
            cursor.execute("UPDATE user SET token = ? WHERE id = ?", (token, user_id))
            conn.commit()
            conn.close()

            _current_user = {'id': user_id, 'name': name, 'email': email, 'role': role, 'token': token}
            save_user_session(_current_user)
            print(f" Connecté : {name} ({role})")
            return _current_user
        else:
            print(" Mot de passe incorrect.")
    else:
        print(" Utilisateur non trouvé.")
    conn.close()
    return None


def logout():
    global _current_user
    if not _current_user:
        print("ℹ️ Aucun utilisateur connecté.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET token = NULL WHERE id = ?", (_current_user["id"],))
    conn.commit()
    conn.close()

    print(f"🔓 Déconnexion de {_current_user['name']}.")
    _current_user = None

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def get_cached_user():
    if not os.path.exists(SESSION_FILE):
        return None

    with open(SESSION_FILE, "r") as f:
        utilisateur = json.load(f)

    if not utilisateur.get("token"):
        return None

    if not is_token_valid(utilisateur["token"]):
        return None

    return utilisateur


def save_user_session(utilisateur):
    with open(SESSION_FILE, "w") as f:
        json.dump(utilisateur, f)
