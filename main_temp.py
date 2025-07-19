# client_menu.py

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box

# Import des fonctions de menu
from menu_client import (
    menu_create_client,
    menu_update_client,
    menu_delete_client,
    menu_list_clients,
    menu_list_all_clients  # 👈 à ajouter si pas encore fait
)

console = Console()

def afficher_menu_client():
    console.print(Panel.fit(
        "[bold cyan]=== Menu Client ===[/bold cyan]\n"
        "[green]1.[/green] Ajouter un client\n"
        "[green]2.[/green] Modifier un client\n"
        "[green]3.[/green] Supprimer un client\n"
        "[green]4.[/green] Voir mes clients\n"
        "[green]5.[/green] Voir tous les clients\n"
        "[green]6.[/green] Quitter",
        title="Gestion des clients",
        border_style="bright_blue",
        box=box.ROUNDED
    ))

def menu_client(utilisateur):
    while True:
        afficher_menu_client()
        choix = Prompt.ask("Que voulez-vous faire ?", choices=["1", "2", "3", "4", "5", "6"])

        if choix == "1":
            menu_create_client(utilisateur)
        elif choix == "2":
            menu_update_client(utilisateur)
        elif choix == "3":
            menu_delete_client(utilisateur)
        elif choix == "4":
            menu_list_clients(utilisateur)
        elif choix == "5":
            menu_list_all_clients(utilisateur)
        elif choix == "6":
            console.print("[cyan]Retour au menu principal ou fin du programme.[/cyan]\n")
            break
