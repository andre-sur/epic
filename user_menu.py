# menu.py
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from users_crud import create_user, update_user, delete_user, display_users

console = Console()

def display_menu_users(utilisateur):
    if utilisateur['role'] != 'gestion':
        console.print("[red]❌ Accès refusé. Seuls les utilisateurs avec le rôle 'gestion' peuvent gérer les utilisateurs.[/red]")
        console.input("Appuyez sur Entrée pour continuer...")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        console.rule("[bold cyan]Menu Gestion des utilisateurs[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Créer un utilisateur")
        table.add_row("2.", "Modifier un utilisateur")
        table.add_row("3.", "Supprimer un utilisateur")
        table.add_row("4.", "Afficher les utilisateurs")
        table.add_row("5.", "Quitter le menu utilisateurs")
        console.print(table)

        choix = Prompt.ask("Choisissez une option", choices=["1", "2", "3", "4", "5"])

        if choix == '1':
            create_user()
        elif choix == '2':
            update_user()
        elif choix == '3':
            delete_user()
        elif choix == '4':
            display_users()
        elif choix == '5':
            break

# Exemple d'appel (à adapter selon ton système d'authentification)
if __name__ == "__main__":
    utilisateur_exemple = {"id": 1, "name": "Admin", "role": "gestion"}
    display_menu_users(utilisateur_exemple)
