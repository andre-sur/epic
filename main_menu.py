import os
import menu_commercial, menu_commercial_rich
import menu_gestion, menu_gestion_rich
import menu_support
import time

# Fonction pour afficher le menu principal
def afficher_menu_principal():
    os.system('cls' if os.name == 'nt' else 'clear')  # Efface l'écran pour un affichage propre
    print("========================================")
    print("           MENU PRINCIPAL")
    print("========================================")
    print("1. Département Commercial")
    print("2. Département Gestion")
    print("3. Département Support")
    print("4. Quitter")
    print("========================================")
    
    choix = input("Veuillez sélectionner une option (1-4) : ")
    return choix

# Fonction principale pour naviguer dans le menu
import os
import menu_commercial
import menu_gestion
import menu_support
from auth import connecter_utilisateur

def main():
    utilisateur = None

    # Boucle de connexion
    while not utilisateur:
        utilisateur = connecter_utilisateur()

    if utilisateur.get('token'):
        print(f"🔐 Votre token est : {utilisateur['token']}")
        print("💡 Conservez-le précieusement. Il va s'effacer dans 60 secondes.")

    # Nettoie l'écran
    time.sleep(60)
    os.system('cls' if os.name == 'nt' else 'clear')

    # Redirection automatique selon le rôle
    role = utilisateur['role']

    if role == 'commercial':
        menu_commercial_rich.afficher_menu_commercial(utilisateur)
    elif role == 'gestion':
        menu_gestion_rich.afficher_menu_gestion(utilisateur)
    elif role == 'support':
        menu_support.afficher_menu_support(utilisateur)
    else:
        print("⛔️ Rôle inconnu. Accès refusé.")

if __name__ == "__main__":
    main()
