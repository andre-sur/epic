import os
import time
from auth import connecter_utilisateur, deconnecter_utilisateur
from token_manager import generer_token_pour_utilisateur, clear_token_pour_utilisateur, save_session, clear_session
import menu_commercial_rich
import menu_gestion_rich
import menu_support_rich

def main():
    utilisateur = None

    while True:
        utilisateur = connecter_utilisateur()
        if not utilisateur:
            print("⛔️ Échec de la connexion, réessayez.")
            continue

        # Génération du token
        token = generer_token_pour_utilisateur(utilisateur['id'])
        save_session(utilisateur['id'], token)
        utilisateur['token'] = token

        print(f"🔐 Votre token est : {utilisateur['token']}")
        print("💡 Conservez-le précieusement. Il va s'effacer dans 10 secondes.")
        time.sleep(10)
        os.system('cls' if os.name == 'nt' else 'clear')

        while True:
            print("\n=== Menu utilisateur ===")
            print("1. Choisir interface (menus ou CLI)")
            print("2. Déconnexion")
            choix = input("Votre choix (1-2) : ").strip()

            if choix == '1':
                role = utilisateur['role']

                print("Choisissez votre interface :")
                print("1. Menu avancé Rich")
                print("2. CLI en ligne de commande")
                choix_interface = input("Votre choix (1-2) : ").strip()

                if choix_interface == '2':
                    print("\n🚀 Vous quittez le menu principal. La CLI démarre.")
                    if role == 'commercial':
                        os.system('python client_cli.py')
                    elif role == 'gestion':
                        os.system('python cli_gestion.py')
                    elif role == 'support':
                        os.system('python event_cli.py')
                    else:
                        print("⛔️ Rôle inconnu. Accès refusé.")
                    print("\n🔙 Vous êtes de retour dans le terminal principal.")
                    exit(0)

                elif choix_interface == '1':
                    if role == 'commercial':
                        menu_commercial_rich.afficher_menu_commercial(utilisateur)
                    elif role == 'gestion':
                        menu_gestion_rich.afficher_menu_gestion(utilisateur)
                    elif role == 'support':
                        menu_support_rich.afficher_menu_support(utilisateur)
                    else:
                        print("⛔️ Rôle inconnu. Accès refusé.")
                else:
                    print("Choix invalide.")

            elif choix == '2':
                clear_token_pour_utilisateur(utilisateur['id'])
                clear_session()
                deconnecter_utilisateur()
                print("✅ Déconnecté.")
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            else:
                print("Choix invalide.")

if __name__ == "__main__":
    main()
