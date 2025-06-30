import sqlite3
import getpass
import bcrypt
import os
import secrets
import time
import pyperclip 

DB_PATH = 'epic_crm.db'

def generer_token_pour_utilisateur(user_id):
    token = secrets.token_hex(16)  # Token aléatoire de 32 caractères
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE user SET token = ? WHERE id = ?", (token, user_id))
    conn.commit()
    conn.close()
    return token

def connecter_utilisateur():
    print("=== Authentification ===")
    print("1. Par email et mot de passe")
    print("2. Par token (EPIC_TOKEN ou saisie manuelle)")

    choix = input("Choix (1 ou 2) : ").strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if choix == '2':
        email = input("Email : ").strip()
        cursor.execute("SELECT id, name, email, role, token FROM user WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user:
            print("❌ Utilisateur non trouvé.")
            return None
        user_id, name, email, role, token_en_base = user

        if not token_en_base:
            print("Vous n'avez pas encore de token.")
            reponse = input("Voulez-vous générer un nouveau token ? (o/n) : ").lower()
            if reponse == 'o':
                token_genere = generer_token_pour_utilisateur(user_id)
                print("✅ Token généré avec succès.")

                # Options de gestion du token
                print("\nComment souhaitez-vous gérer votre token ?")
                print("1. Sauvegarder dans un fichier texte")
                print("2. Copier dans le presse-papiers")
                print("3. Afficher pendant 60 secondes")

                action = input("Votre choix (1/2/3) : ").strip()

                if action == '1':
                    with open("mon_token.txt", "w") as f:
                        f.write(token_genere)
                    print("💾 Token enregistré dans 'mon_token.txt'.")
                elif action == '2':
                    try:
                        pyperclip.copy(token_genere)
                        print("📋 Token copié dans le presse-papiers.")
                    except Exception:
                        print("⚠️ Impossible de copier dans le presse-papiers (module pyperclip non fonctionnel).")
                elif action == '3':
                    print(f"⌛ Votre token : {token_genere}")
                    print("Il sera effacé de l'écran dans 60 secondes...")
                    time.sleep(60)
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    print("Aucune action effectuée.")

                return {'id': user_id, 'name': name, 'email': email, 'role': role}
            else:
                print("Authentification par token annulée.")
                return None
        else:
            token = os.environ.get('EPIC_TOKEN')
            if not token:
                token = input("Token : ").strip()

            if token == token_en_base:
                print(f"🔐 Connecté avec token – {email}")
                return {'id': user_id, 'name': name, 'email': email, 'role': role}
            else:
                print("❌ Token invalide.")
                return None

    elif choix == '1':
        email = input("Email : ").strip()
        password = getpass.getpass("Mot de passe : ").encode('utf-8')

        cursor.execute("SELECT id, name, email, password, role FROM user WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            user_id, name, email, hashed_password, role = row
            if bcrypt.checkpw(password, hashed_password.encode('utf-8')):
                print(f"✅ Connecté avec succès – {name} ({role})")
                return {'id': user_id, 'name': name, 'email': email, 'role': role}
            else:
                print("❌ Mot de passe incorrect.")
        else:
            print("❌ Utilisateur non trouvé.")
        return None

    else:
        print("❌ Choix invalide.")
        return None
