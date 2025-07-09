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

def main():
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

        print("\n=== Menu utilisateur ===")
        print(f"\n👤 Connecté en tant que : {utilisateur['name']} ({utilisateur['role']})")

        print("1. Menu Contrat")
        print("2. Menu Client")
        print("3. Menu Evenement")
        print("4. Menu Collaborateurs")
        print("5. CLI")
        print("6. Déconnexion")

        choix_interface = input("Votre choix (1-2) : ").strip()

        if choix_interface == '5':
                    print("\n🚀 Vous quittez le menu principal. La CLI démarre.")
                    os.system('python client_cli.py')
                    os.system('python contract_cli.py')
                    print("\n🔙 Vous êtes de retour dans le terminal principal.")
                    exit(0)

        elif choix_interface == '1':
                        menu_contract.afficher_menu_contrat(utilisateur)
                
        elif choix_interface == '2':
                        menu_client.afficher_menu_client(utilisateur)
                
        elif choix_interface == '3':
                        menu_event.afficher_menu_event(utilisateur)
               
        elif choix_interface == '4':
                        menu_user.display_menu_users(utilisateur)
        elif choix_interface == '6':
                    clear_token_pour_utilisateur(utilisateur['id'])
                    clear_session()
                    deconnecter_utilisateur()
                    print("✅ Token supprimé, utilisateur déconnecté.")
                    #os.system('cls' if os.name == 'nt' else 'clear')
                    break
        else:
                    print("Choix invalide.")

if __name__ == "__main__":
    main()
