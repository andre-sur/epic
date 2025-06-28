import sqlite3
from functions import create_user, login, check_role, get_clients_for_commercial, get_events_for_support
import sentry_sdk

# Initialisation de Sentry (remplacer avec ta propre clé DSN de Sentry)
sentry_sdk.init("https://your-sentry-dsn-url")

# -------- Menu principal --------

def menu():
    while True:
        try:
            print("\n--- Menu Principal ---")
            print("1. Créer un utilisateur")
            print("2. Se connecter")
            print("3. Quitter")
            
            choix = input("Choisissez une option : ")

            if choix == "1":
                name = input("Nom complet : ")
                email = input("Email : ")
                password = input("Mot de passe : ")
                role = input("Rôle (commercial/support/gestion) : ")
                create_user(name, email, password, role)

            elif choix == "2":
                email = input("Entrez votre email : ")
                password = input("Entrez votre mot de passe : ")
                user = login(email, password)
                
                if user:
                    print(f"Bienvenue {user[1]} !")
                    user_role = user[3]  # Récupérer le rôle de l'utilisateur
                    print(f"Votre rôle est : {user_role}")

                    # En fonction du rôle de l'utilisateur, afficher les options spécifiques
                    if check_role(user, 'commercial'):
                        print("Accès au menu commercial.")
                        commercial_id = user[0]  # Supposons que l'ID de l'utilisateur soit dans user[0]
                        clients = get_clients_for_commercial(commercial_id)
                        if clients:
                            for client in clients:
                                print(client)
                        else:
                            print("Aucun client trouvé.")

                    elif check_role(user, 'support'):
                        print("Accès au menu support.")
                        support_id = user[0]
                        events = get_events_for_support(support_id)
                        if events:
                            for event in events:
                                print(event)
                        else:
                            print("Aucun événement trouvé.")

                    elif check_role(user, 'gestion'):
                        print("Accès au menu gestion.")
                        # Actions spécifiques pour le gestionnaire
                        pass

                    else:
                        print("Rôle non reconnu.")
                else:
                    print("Identifiants incorrects.")
            
            elif choix == "3":
                print("Au revoir!")
                break
            else:
                print("Option invalide, veuillez réessayer.")
        
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("Une erreur inattendue est survenue. Veuillez réessayer plus tard.")

# Lancer le menu principal
if __name__ == "__main__":
    menu()
