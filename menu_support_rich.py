import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_support(utilisateur):
    while True:
        console.clear()
        console.rule(f"[bold cyan]Menu Support – Bienvenue {utilisateur['name']}[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Voir mes événements")
        table.add_row("2.", "Mettre à jour un événement")
        table.add_row("3.", "Afficher tous les événements")
        table.add_row("4.", "Retour au menu principal")
        console.print(table)

        choix = Prompt.ask("Veuillez entrer votre choix", choices=["1", "2", "3", "4"])

        if choix == "1":
            voir_evenements_attribues(utilisateur)
        elif choix == "2":
            mettre_a_jour_evenement(utilisateur)
        elif choix == "3":
            afficher_evenements()
        elif choix == "4":
            break

def voir_evenements_attribues(utilisateur):
    console.print(f"[bold green]=== Vos événements (Support ID: {utilisateur['id']}) ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, contract_id, start_date, end_date, location FROM event WHERE support_id = ?", (utilisateur['id'],))
    events = cursor.fetchall()
    conn.close()

    if not events:
        console.print("[yellow]Aucun événement trouvé.[/yellow]")
    else:
        table = Table(title="Événements attribués", header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Contrat ID")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")

        for e in events:
            table.add_row(str(e[0]), str(e[1]), e[2], e[3], e[4])
        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

def mettre_a_jour_evenement(utilisateur):
    console.print("[bold green]=== Mise à jour d'un événement ===[/bold green]")
    event_id = Prompt.ask("ID de l'événement à mettre à jour")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier si l'événement existe
    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    if not event:
        console.print("[red]Erreur : Aucun événement avec cet ID.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    # Vérifier si l'événement appartient au support connecté
    cursor.execute("SELECT * FROM event WHERE id = ? AND support_id = ?", (event_id, utilisateur['id']))
    autorise = cursor.fetchone()
    if not autorise:
        console.print("[red]Vous n'avez pas la permission de modifier cet événement.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    start_date = Prompt.ask("Nouvelle date de début (laisser vide pour ne pas modifier)", default="")
    end_date = Prompt.ask("Nouvelle date de fin (laisser vide pour ne pas modifier)", default="")
    location = Prompt.ask("Nouveau lieu (laisser vide pour ne pas modifier)", default="")

    if start_date:
        cursor.execute("UPDATE event SET start_date = ? WHERE id = ?", (start_date, event_id))
    if end_date:
        cursor.execute("UPDATE event SET end_date = ? WHERE id = ?", (end_date, event_id))
    if location:
        cursor.execute("UPDATE event SET location = ? WHERE id = ?", (location, event_id))

    conn.commit()
    conn.close()

    console.print("[bold green]Événement mis à jour avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def afficher_evenements():
    console.print("[bold green]=== Liste de tous les événements ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, contract_id, support_id, start_date, end_date, location FROM event")
    events = cursor.fetchall()
    conn.close()

    if not events:
        console.print("[yellow]Aucun événement enregistré.[/yellow]")
    else:
        table = Table(title="Tous les événements", header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Contrat ID")
        table.add_column("Support ID")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")

        for e in events:
            table.add_row(str(e[0]), str(e[1]), str(e[2]), e[3], e[4], e[5])
        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

# Exemple d’appel pour test
if __name__ == "__main__":
    utilisateur_support = {"id": 2, "name": "Support_User"}
    afficher_menu_support(utilisateur_support)
