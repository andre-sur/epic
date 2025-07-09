import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_event(utilisateur):
    while True:
        console.clear()
        console.rule(f"[bold cyan]Menu Événements – Bienvenue {utilisateur['name']}[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Créer un événement (commercial)")
        table.add_row("2.", "Modifier un événement (gestion, support)")
        table.add_row("3.", "Supprimer un événement (gestion)")
        table.add_row("4.", "Afficher mes événements (tous)")
        table.add_row("5.", "Afficher tous les événements (tous)")
        table.add_row("6.", "[red]Retour au menu précédent[/red]")
        console.print(table)

        choix = Prompt.ask("Veuillez entrer votre choix", choices=["1", "2", "3", "4", "5"])

        if choix == "1":
            if utilisateur['role'] == 'commercial':
                add_event(utilisateur)
            else:
                console.print("[red]Vous n'avez pas la permission de créer un événement.[/red]")
                console.input("Appuyez sur Entrée pour continuer...")

        elif choix == "2":
            if utilisateur['role'] == 'gestion' or utilisateur['role'] == 'support':
                update_event(utilisateur)
            else:
                console.print("[red]Vous n'avez pas la permission de modifier un événement.[/red]")
                console.input("Appuyez sur Entrée pour continuer...")

        elif choix == "3":
            if utilisateur['role'] == 'gestion':
                delete_event(utilisateur)
            else:
                console.print("[red]Vous n'avez pas la permission de supprimer un événement.[/red]")
                console.input("Appuyez sur Entrée pour continuer...")

        elif choix == "4":
            display_my_events(utilisateur)

        elif choix == "5":
            display_all_events()

        elif choix == "6":
            break

def add_event(utilisateur):
    console.print("[bold green]=== Création d'un événement ===[/bold green]")
    contract_id = Prompt.ask("ID du contrat lié")
    start_date = Prompt.ask("Date de début (AAAA-MM-JJ)")
    end_date = Prompt.ask("Date de fin (AAAA-MM-JJ)")
    location = Prompt.ask("Lieu")
    attendees = Prompt.ask("Nombre de participants", default="0")
    notes = Prompt.ask("Notes (facultatif)", default="")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (contract_id, utilisateur['id'], start_date, end_date, location, attendees, notes))

    conn.commit()
    conn.close()

    console.print("[bold green]✅ Événement créé avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def update_event(utilisateur):
    console.print("[bold green]=== Modification d'un événement ===[/bold green]")
    event_id = Prompt.ask("ID de l'événement à modifier")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier que l'événement est lié au support connecté
    cursor.execute("SELECT * FROM event WHERE id = ? AND support_id = ?", (event_id, utilisateur['id']))
    event = cursor.fetchone()

    if not event:
        console.print("[red]Événement introuvable ou non lié à vous.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    colonnes = [desc[0] for desc in cursor.description]
    event_data = dict(zip(colonnes, event))

    console.print("[yellow]Laisser vide pour garder la valeur actuelle.[/yellow]")
    new_contract_id = Prompt.ask(f"ID du contrat [{event_data['contract_id']}]", default=str(event_data['contract_id']))
    new_start = Prompt.ask(f"Date début [{event_data['start_date']}]", default=event_data['start_date'])
    new_end = Prompt.ask(f"Date fin [{event_data['end_date']}]", default=event_data['end_date'])
    new_location = Prompt.ask(f"Lieu [{event_data['location']}]", default=event_data['location'])
    new_attendees = Prompt.ask(f"Participants [{event_data['attendees']}]", default=str(event_data['attendees']))
    new_notes = Prompt.ask(f"Notes [{event_data['notes']}]", default=event_data['notes'] or "")

    cursor.execute("""
        UPDATE event
        SET contract_id = ?, start_date = ?, end_date = ?, location = ?, attendees = ?, notes = ?
        WHERE id = ?
    """, (new_contract_id, new_start, new_end, new_location, new_attendees, new_notes, event_id))

    conn.commit()
    conn.close()

    console.print("[green]✅ Événement modifié avec succès.[/green]")
    console.input("Appuyez sur Entrée pour continuer...")

def delete_event(utilisateur):
    console.print("[bold red]=== Suppression d'un événement ===[/bold red]")
    event_id = Prompt.ask("ID de l'événement à supprimer")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM event WHERE id = ?", (event_id,))
    if not cursor.fetchone():
        console.print("[red]Événement introuvable.[/red]")
    else:
        cursor.execute("DELETE FROM event WHERE id = ?", (event_id,))
        conn.commit()
        console.print("[green]✅ Événement supprimé avec succès.[/green]")

    conn.close()
    console.input("Appuyez sur Entrée pour continuer...")

def display_my_events(utilisateur):
    console.print("[bold green]=== Liste des événements ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()

    # Tout le monde peut voir tous les événements
    cursor.execute("""
        SELECT id, contract_id, support_id, start_date, end_date, location, attendees, notes
        FROM event
    """)
    events = cursor.fetchall()
    conn.close()

    if not events:
        console.print("[yellow]Aucun événement trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Contrat ID")
        table.add_column("Support ID")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")
        table.add_column("Participants")
        table.add_column("Notes")

        for e in events:
            table.add_row(
                str(e[0]), str(e[1]), str(e[2] or "-"), e[3], e[4], e[5], str(e[6] or "0"), e[7] or "-"
            )

        console.print(table)

def display_all_events():
    console.print("[bold green]=== Liste des événements ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()

    # Tout le monde peut voir tous les événements
    cursor.execute("""
        SELECT id, contract_id, support_id, start_date, end_date, location, attendees, notes
        FROM event
    """)
    events = cursor.fetchall()
    conn.close()

    if not events:
        console.print("[yellow]Aucun événement trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Contrat ID")
        table.add_column("Support ID")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")
        table.add_column("Participants")
        table.add_column("Notes")

        for e in events:
            table.add_row(
                str(e[0]), str(e[1]), str(e[2] or "-"), e[3], e[4], e[5], str(e[6] or "0"), e[7] or "-"
            )

        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

# Exemple pour tester
if __name__ == "__main__":
    utilisateur_exemple = {"id": 3, "name": "Luc", "role": "support"}
    afficher_menu_event(utilisateur_exemple)
