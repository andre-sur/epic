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
            display_my_event(utilisateur)
        elif choix == "2":
            update_event(utilisateur)
        elif choix == "3":
            display_event()
        elif choix == "4":
            break

def display_my_event(utilisateur):
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

import sqlite3
from rich.prompt import Prompt

def update_event(utilisateur):
    console.print("[bold green]=== Mise à jour d'un événement ===[/bold green]")
    event_id = Prompt.ask("ID de l'événement à mettre à jour")

    conn = connect_db()
    conn.row_factory = sqlite3.Row   # ✅ permet de récupérer les colonnes par nom
    cursor = conn.cursor()

    # Vérifier si l'événement existe
    cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    if not event:
        console.print("[red]Erreur : Aucun événement avec cet ID.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    # Vérifier si l'événement appartient bien au support connecté
    cursor.execute("SELECT * FROM event WHERE id = ? AND support_id = ?", (event_id, utilisateur['id']))
    autorise = cursor.fetchone()
    if not autorise:
        console.print("[red]Vous n'avez pas la permission de modifier cet événement.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    # Récupérer les valeurs actuelles
    current_start_date = autorise['start_date'] or ""
    current_end_date = autorise['end_date'] or ""
    current_location = autorise['location'] or ""
    current_attendees = str(autorise['attendees']) if autorise['attendees'] is not None else ""
    current_notes = autorise['notes'] or ""

    # Proposer les modifications
    start_date = Prompt.ask(f"Date de début [{current_start_date}]", default="")
    end_date = Prompt.ask(f"Date de fin [{current_end_date}]", default="")
    location = Prompt.ask(f"Lieu [{current_location}]", default="")
    attendees_input = Prompt.ask(f"Nombre de participants [{current_attendees}]", default="")
    notes = Prompt.ask(f"Notes [{current_notes}]", default="")

    # Construire dynamiquement la requête UPDATE
    updates = []
    params = []

    if start_date.strip():
        updates.append("start_date = ?")
        params.append(start_date.strip())
    if end_date.strip():
        updates.append("end_date = ?")
        params.append(end_date.strip())
    if location.strip():
        updates.append("location = ?")
        params.append(location.strip())
    if attendees_input.strip():
        try:
            attendees = int(attendees_input.strip())
            updates.append("attendees = ?")
            params.append(attendees)
        except ValueError:
            console.print("[red]Nombre de participants invalide, modification ignorée.[/red]")
    if notes.strip():
        updates.append("notes = ?")
        params.append(notes.strip())

    if updates:
        sql = f"UPDATE event SET {', '.join(updates)} WHERE id = ?"
        params.append(event_id)
        cursor.execute(sql, params)
        conn.commit()
        console.print("[bold green]Événement mis à jour avec succès ![/bold green]")
    else:
        console.print("[yellow]Aucune modification apportée.[/yellow]")

    conn.close()
    console.input("Appuyez sur Entrée pour continuer...")

def display_event():
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
