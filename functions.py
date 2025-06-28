import sqlite3
import bcrypt
import sentry_sdk

# Initialisation de Sentry (remplacer avec ta propre clé DSN de Sentry)
sentry_sdk.init("https://7f070b8d8417b940e01da3d491c601b8@o4509518763917312.ingest.de.sentry.io/4509518772830288")

# Fonction pour créer un utilisateur
def create_user(name, email, password, role):
    try:
        # Hachage du mot de passe
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Connexion à la base de données
        conn = sqlite3.connect("epic_crm.db")
        cursor = conn.cursor()

        # Insertion dans la base de données
        cursor.execute('''
            INSERT INTO user (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', (name, email, hashed_pw, role))

        conn.commit()
        conn.close()
        print(f"Utilisateur {name} créé avec succès.")

    except sqlite3.Error as e:
        sentry_sdk.capture_exception(e)  # Capture l'exception dans Sentry
        print("Erreur lors de la création de l'utilisateur. Vérifiez les logs.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Une erreur inconnue est survenue : {e}")

# Fonction pour se connecter
def login(email, password):
    try:
        conn = sqlite3.connect("epic_crm.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            conn.close()
            return user
        else:
            conn.close()
            return None

    except sqlite3.Error as e:
        sentry_sdk.capture_exception(e)
        print("Erreur de base de données lors de la connexion.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Une erreur inconnue est survenue lors de la connexion : {e}")

# Vérification du rôle de l'utilisateur
def check_role(user, required_role):
    try:
        if user and user[3] == required_role:
            return True
        return False
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print("Erreur lors de la vérification du rôle.")
        return False

# Fonction pour récupérer les clients d'un commercial
def get_clients_for_commercial(commercial_id):
    try:
        conn = sqlite3.connect("epic_crm.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client WHERE commercial_id = ?", (commercial_id,))
        clients = cursor.fetchall()
        conn.close()
        return clients

    except sqlite3.Error as e:
        sentry_sdk.capture_exception(e)
        print("Erreur de base de données lors de la récupération des clients.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Une erreur inconnue est survenue lors de la récupération des clients : {e}")

# Fonction pour récupérer les événements d'un support
def get_events_for_support(support_id):
    try:
        conn = sqlite3.connect("epic_crm.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM event WHERE support_id = ?", (support_id,))
        events = cursor.fetchall()
        conn.close()
        return events

    except sqlite3.Error as e:
        sentry_sdk.capture_exception(e)
        print("Erreur de base de données lors de la récupération des événements.")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Une erreur inconnue est survenue lors de la récupération des événements : {e}")
