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
            print("1. Choisir interface (menus ou Command-Line-Interface)")
            print("2. Déconnexion")
            choix = input("Votre choix (1-2) : ").strip()

            if choix == '1':
                role = utilisateur['role']

                print("Choisissez votre interface :")
                print("1. Menu avancé Rich")
                print("2. CLI en ligne de commande")
                choix_interface = input("Votre choix (1-2) : ").strip()

                if choix_interface == '2':
                    print("\n🚀 Vous avez quitté le menu principal. La CLI va maintenant démarrer.")
                    print("🖥️ Une fois la CLI terminée, vous reviendrez ici dans le terminal.")
                    if role == 'commercial':
                        os.system('python cli_commercial.py')
                    elif role == 'gestion':
                        os.system('python cli_gestion.py')
                    elif role == 'support':
                        os.system('python cli_support.py')
                    else:
                        print("⛔️ Rôle inconnu. Accès refusé.")
                    print("\n🔙 Vous êtes de retour dans le terminal principal.")
                    break  # Sortie de la boucle menu utilisateur, retour au terminal principal

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
                # Déconnexion : suppression du token (si implémenté)
                deconnecter_utilisateur()
                print("✅ Déconnecté.")
                os.system('cls' if os.name == 'nt' else 'clear')
                break  # Retour à la boucle de connexion
            else:
                print("Choix invalide.")

if __name__ == "__main__":
    main()
