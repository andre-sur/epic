import os
import time
from auth import connecter_utilisateur, deconnecter_utilisateur
from token_manager import generer_token_pour_utilisateur, clear_token_pour_utilisateur, save_session, clear_session
import menu_commercial_rich
import menu_gestion_rich
import menu_contract
import menu_client
import menu_event
import menu_user

def login():
    utilisateur = None

    while True:
        utilisateur = connecter_utilisateur()
        if not utilisateur:
            print("⛔️ Échec de la connexion, réessayez.")
            continue

        # Génération du token
        token = generer_token_pour_utilisateur(utilisateur['id'])
        save_session(utilisateur['id'], token, utilisateur['role'],utilisateur['name'])
        utilisateur['token'] = token

        print(f"🔐 Votre token est : {utilisateur['token']}")
        print("💡 Il est conservé le temps de la session.")
        time.sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        role = utilisateur['role']