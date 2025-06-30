import os
import time
from auth import connecter_utilisateur, deconnecter_utilisateur
import menu_commercial_rich
import menu_gestion_rich
import menu_support_rich

def main():
    utilisateur = None

    while True:
        # Connexion utilisateur
        utilisateur = connecter_utilisateur()
        if not utilisateur:
            print("⛔️ Échec de la connexion, réessayez.")
            continue

        # Affiche le token temporairement si présent
        if utilisateur.get('token'):
            print(f"🔐 Votre token est : {utilisateur['token']}")
            print("💡 Conservez-le précieusement. Il va s'effacer dans 60 secondes.")
            time.sleep(60)
            os.system('cls' if os.name == 'nt' else 'clear')

        # Menu après connexion
        while True:
            print("\n=== Menu utilisateur ===")
            print("1. Choisir interface")
            print("2. Déconnexion")
            choix = input("Votre choix (1-2) : ").strip()

            if choix == '1':
                role = utilisateur['role']

                print("Choisissez votre interface :")
                print("1. Menu avancé Rich")
                print("2. CLI en ligne de commande")
                choix_interface = input("Votre choix (1-2) : ").strip()

                if role == 'commercial':
                    if choix_interface == '1':
                        menu_commercial_rich.afficher_menu_commercial(utilisateur)
                    elif choix_interface == '2':
                        os.system('python cli_commercial.py')
                    else:
                        print("Choix invalide.")
                elif role == 'gestion':
                    if choix_interface == '1':
                        menu_gestion_rich.afficher_menu_gestion(utilisateur)
                    elif choix_interface == '2':
                        os.system('python cli_gestion.py')
                    else:
                        print("Choix invalide.")
                elif role == 'support':
                    if choix_interface == '1':
                        menu_support_rich.afficher_menu_support(utilisateur)
                    elif choix_interface == '2':
                        os.system('python cli_support.py')
                    else:
                        print("Choix invalide.")
                else:
                    print("⛔️ Rôle inconnu. Accès refusé.")
            elif choix == '2':
                # Déconnexion : suppression du token (si implémenté)
                deconnecter_utilisateur(utilisateur['id'])
                print("✅ Déconnecté.")
                os.system('cls' if os.name == 'nt' else 'clear')
                break  # Retour à la boucle de connexion
            else:
                print("Choix invalide.")

if __name__ == "__main__":
    main()
