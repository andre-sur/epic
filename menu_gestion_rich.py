import sqlite3
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_gestion(utilisateur):
    while True:
        console.print(f"\n[bold cyan]Menu Gestion – Bienvenue {utilisateur['name']}[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option", style="dim")
        table.add_column("Action")
        table.add_row("1", "Créer un collaborateur")
        table.add_row("2", "Mettre à jour un collaborateur")
        table.add_row("3", "Afficher tous les collaborateurs")
        table.add_row("4", "Créer un événement")
        table.add_row("5", "Filtrer les événements")
        table.add_row("6", "Retour au menu principal")
        console.print(table)

        choix = input("Veuillez entrer votre choix: ")

        if choix == '1':
            creer_collaborateur()
        elif choix == '2':
            mettre_a_jour_collaborateur()
        elif choix == '3':
            afficher_collaborateurs()
        elif choix == '4':
            creer_evenement()
        elif choix == '5':
            filtrer_evenements()
        elif choix == '6':
            break
        else:
            console.print("[red]Choix invalide. Veuillez réessayer.[/red]")

def creer_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()
    console.print("[bold yellow]=== Création d'un collaborateur ===[/bold yellow]")
    name = input("Nom du collaborateur: ")
    email = input("Email du collaborateur: ")
    password = input("Mot de passe du collaborateur: ")
    role = input("Rôle (gestion, commercial, support): ")

    cursor.execute("""
        INSERT INTO user (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, role))

    conn.commit()
    console.print("[green]Collaborateur ajouté avec succès ![/green]")
    conn.close()

def mettre_a_jour_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()
    console.print("[bold yellow]=== Mise à jour d'un collaborateur ===[/bold yellow]")
    collaborator_id = input("ID du collaborateur à mettre à jour: ")

    cursor.execute("SELECT * FROM user WHERE id = ?", (collaborator_id,))
    user = cursor.fetchone()
    if not user:
        console.print("[red]Aucun collaborateur avec cet ID.[/red]")
        conn.close()
        return

    name = input("Nouveau nom (laisser vide pour ne pas modifier): ")
    email = input("Nouveau email (laisser vide pour ne pas modifier): ")

    if name:
        cursor.execute("UPDATE user SET name = ? WHERE id = ?", (name, collaborator_id))
    if email:
        cursor.execute("UPDATE user SET email = ? WHERE id = ?", (email, collaborator_id))

    conn.commit()
    console.print("[green]Collaborateur mis à jour avec succès.[/green]")
    conn.close()

def afficher_collaborateurs():
    conn = connect_db()
    cursor = conn.cursor()
    console.print("[bold yellow]=== Liste des collaborateurs ===[/bold yellow]")
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()

    if not users:
        console.print("[red]Aucun collaborateur trouvé.[/red]")
    else:
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("ID", style="dim")
        table.add_column("Nom")
        table.add_column("Email")
        table.add_column("Rôle")
        for user in users:
            table.add_row(str(user[0]), user[1], user[2], user[4])
        console.print(table)

    conn.close()

def creer_evenement():
    conn = connect_db()
    cursor = conn.cursor()
    console.print("[bold yellow]=== Création d'un événement ===[/bold yellow]")

    contract_id = input("ID du contrat lié à cet événement: ")
    support_id = input("ID du collaborateur du support responsable: ")
    start_date = input("Date de début (AAAA-MM-JJ HH:MM): ")
    end_date = input("Date de fin (AAAA-MM-JJ HH:MM): ")

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        if end_dt <= start_dt:
            console.print("[red]Erreur : la date de fin doit être postérieure à la date de début.[/red]")
            return
    except ValueError:
        console.print("[red]Format de date invalide. Utilisez AAAA-MM-JJ HH:MM.[/red]")
        return

    location = input("Lieu de l'événement: ")
    attendees = int(input("Nombre d'attendees: "))
    notes = input("Notes supplémentaires: ")

    cursor.execute("""
        INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (contract_id, support_id, start_date, end_date, location, attendees, notes))

    conn.commit()
    console.print("[green]Événement créé avec succès ![/green]")
    conn.close()

def filtrer_evenements():
    conn = connect_db()
    cursor = conn.cursor()
    console.print("[bold yellow]=== Filtrer les événements ===[/bold yellow]")
    filtre = input("Filtrer par date de début (ex: 2023-05-01): ")

    cursor.execute("SELECT * FROM event WHERE start_date >= ?", (filtre,))
    events = cursor.fetchall()

    if not events:
        console.print("[red]Aucun événement trouvé pour cette date.[/red]")
    else:
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID")
        table.add_column("Contrat ID")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")
        table.add_column("Participants")
        for event in events:
            table.add_row(
                str(event[0]), str(event[1]), event[3], event[4], event[5], str(event[6])
            )
        console.print(table)

    conn.close()
