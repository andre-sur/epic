import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

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
    
def update_event(utilisateur):
    console.print("[bold green]=== Modification d'un événement ===[/bold green]")
    event_id = Prompt.ask("ID de l'événement à modifier")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier si l'événement existe et est accessible
    if utilisateur['role'] == 'gestion':
        cursor.execute("SELECT * FROM event WHERE id = ?", (event_id,))
    else:
        cursor.execute("SELECT * FROM event WHERE id = ? AND support_id = ?", (event_id, utilisateur['id']))

    event = cursor.fetchone()

    if not event:
        console.print("[red]Événement introuvable ou non lié à vous.[/red]")
        conn.close()
        return

    # On extrait les colonnes (d’après l’ordre du SELECT *)
    _, contract_id, support_id, start_date, end_date, location, attendees, notes = event

    if utilisateur['role'] == 'gestion':
        console.print(f"[cyan]Événement actuel : support_id={support_id}[/cyan]")
        
        while True:
            new_support_id = Prompt.ask(
                "ID du nouveau support associé",
                default=str(support_id) if support_id else ""
            )

            # Vérifier que cet ID existe et qu'il correspond bien à un user avec rôle 'support'
            cursor.execute("SELECT id FROM user WHERE id = ? AND role = 'support'", (new_support_id,))
            result = cursor.fetchone()

            if result:
                # OK, l'ID est valide
                cursor.execute("UPDATE event SET support_id = ? WHERE id = ?", (new_support_id, event_id))
                conn.commit()
                console.print("[green]✅ Support associé modifié avec succès.[/green]")
                break
            else:
                console.print("[red]❌ ID invalide ou cet utilisateur n'est pas un support. Veuillez réessayer.[/red]")


    else:
        console.print(f"[cyan]Événement actuel :\n"
                      f"Start date: {start_date}, End date: {end_date}, "
                      f"Location: {location}, Attendees: {attendees}, Notes: {notes}[/cyan]")

        new_start_date = Prompt.ask("Nouvelle date de début (AAAA-MM-JJ)", default=start_date)
        new_end_date = Prompt.ask("Nouvelle date de fin (AAAA-MM-JJ)", default=end_date)
        new_location = Prompt.ask("Nouveau lieu", default=location)
        new_attendees = Prompt.ask("Nombre de participants", default=str(attendees))
        new_notes = Prompt.ask("Notes", default=notes or "")

        cursor.execute("""
            UPDATE event
            SET start_date = ?, end_date = ?, location = ?, attendees = ?, notes = ?
            WHERE id = ?
        """, (new_start_date, new_end_date, new_location, int(new_attendees), new_notes, event_id))

        conn.commit()
        console.print("[green]✅ Événement modifié avec succès.[/green]")

    conn.close()
   # console.input("Appuyez sur Entrée pour continuer...")

def delete_event(utilisateur):
    console.print("[bold red]=== Suppression d'un événement ===[/bold red]")
    event_id = Prompt.ask("ID de l'événement à supprimer")

    conn = connect_db()
    cursor = conn.cursor()

    # Récupérer toutes les infos de l'événement
    cursor.execute("""
        SELECT id, contract_id, support_id, start_date, end_date, location, attendees, notes
        FROM event WHERE id = ?
    """, (event_id,))
    event = cursor.fetchone()

    if not event:
        console.print("[red]❌ Événement introuvable.[/red]")
        conn.close()
        return

    # Afficher un récapitulatif sous forme de tableau
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Champ")
    table.add_column("Valeur")

    champs = ["ID", "Contrat ID", "Support ID", "Début", "Fin", "Lieu", "Participants", "Notes"]
    for champ, valeur in zip(champs, event):
        table.add_row(champ, str(valeur) if valeur is not None else "-")

    console.print(table)

    # Demander confirmation
    confirm = Prompt.ask(f"[yellow]Voulez-vous vraiment supprimer cet événement ? (o/n)[/yellow]", choices=['o', 'n'])
    if confirm == 'o':
        cursor.execute("DELETE FROM event WHERE id = ?", (event_id,))
        conn.commit()
        console.print("[green]✅ Événement supprimé avec succès.[/green]")
    else:
        console.print("[yellow]Suppression annulée.[/yellow]")

    conn.close()
    

def display_my_events(utilisateur):
    console.print("[bold green]=== Liste des événements ===[/bold green]")
    conn = connect_db()
    cursor = conn.cursor()

    if utilisateur:
        cursor.execute("""
            SELECT id, contract_id, support_id, start_date, end_date, location, attendees, notes 
            FROM event
            WHERE support_id = ?
    """, (utilisateur['id'],))
        console.print("Mes événements")

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

def display_all_events(utilisateur):
    console.print("[bold green]=== Liste de tous les événements ===[/bold green]")
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, contract_id, support_id, start_date, end_date, location, attendees, notes FROM event")
    console.print("Tous les événements")
    
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


def display_events_nosupport(utilisateur):
    console.print("[bold green]=== Liste des événements ===[/bold green]")
    conn = connect_db()
    cursor = conn.cursor()

    if utilisateur:
        cursor.execute("""
            SELECT id, contract_id, support_id, start_date, end_date, location, attendees, notes 
            FROM event
            WHERE support_id IS NULL
    """)
        console.print("Evenements sans affectation d'un Support")

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
  
