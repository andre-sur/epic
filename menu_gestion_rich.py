import sqlite3
from datetime import datetime
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_gestion(utilisateur):
    if utilisateur["role"] != "gestion":
        print("[red]Accès refusé : ce menu est réservé aux gestionnaires.[/red]")
        return

    while True:
        console.print(f"\n[bold cyan]Menu Gestion – Bienvenue {utilisateur['name']}[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Option", justify="center")
        table.add_column("Description")
        table.add_row("1", "Créer un collaborateur")
        table.add_row("2", "Mettre à jour un collaborateur")
        table.add_row("3", "Afficher tous les collaborateurs")
        table.add_row("4", "Créer un événement")
        table.add_row("5", "Filtrer les événements")
        table.add_row("6", "Retour au menu principal")
        console.print(table)

        choix = input("Veuillez entrer votre choix: ")

        if choix == "1":
            creer_collaborateur()
        elif choix == "2":
            mettre_a_jour_collaborateur()
        elif choix == "3":
            afficher_collaborateurs()
        elif choix == "4":
            creer_evenement()
        elif choix == "5":
            filtrer_evenements()
        elif choix == "6":
            break
        else:
            print("[red]Choix invalide. Veuillez réessayer.[/red]")

def creer_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un collaborateur ===")
    name = input("Nom du collaborateur: ")
    email = input("Email: ")
    password = input("Mot de passe: ")
    role = input("Rôle (gestion, commercial, support): ").strip().lower()

    if role not in ["gestion", "commercial", "support"]:
        print("[red]Rôle invalide.[/red]")
        conn.close()
        return

    cursor.execute("INSERT INTO user (name, email, password, role) VALUES (?, ?, ?, ?)", (name, email, password, role))
    conn.commit()
    print("[green]Collaborateur ajouté avec succès ![/green]")
    conn.close()

def mettre_a_jour_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Mise à jour d'un collaborateur ===")
    id_ = input("ID du collaborateur: ")
    cursor.execute("SELECT * FROM user WHERE id = ?", (id_,))
    user = cursor.fetchone()

    if not user:
        print("[red]Aucun collaborateur avec cet ID.[/red]")
        conn.close()
        return

    name = input("Nouveau nom (laisser vide): ")
    email = input("Nouvel email (laisser vide): ")

    if name:
        cursor.execute("UPDATE user SET name = ? WHERE id = ?", (name, id_))
    if email:
        cursor.execute("UPDATE user SET email = ? WHERE id = ?", (email, id_))

    conn.commit()
    print("[green]Collaborateur mis à jour avec succès ![/green]")
    conn.close()

def afficher_collaborateurs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()

    if not users:
        print("[yellow]Aucun collaborateur trouvé.[/yellow]")
    else:
        table = Table(title="Collaborateurs")
        table.add_column("ID", justify="center")
        table.add_column("Nom", justify="left")
        table.add_column("Email", justify="left")
        table.add_column("Rôle", justify="center")

        for u in users:
            table.add_row(str(u[0]), u[1], u[2], u[4])

        console.print(table)

    conn.close()

def creer_evenement():
    conn = connect_db()
    cursor = conn.cursor()

    print("=== Création d'un événement ===")
    contract_id = input("ID du contrat lié: ")
    support_id = input("ID du support: ")

    cursor.execute("SELECT * FROM contract WHERE id = ?", (contract_id,))
    if not cursor.fetchone():
        print("[red]Contrat introuvable.[/red]")
        conn.close()
        return

    cursor.execute("SELECT * FROM user WHERE id = ? AND role = 'support'", (support_id,))
    if not cursor.fetchone():
        print("[red]Support introuvable.[/red]")
        conn.close()
        return

    start_date = input("Début (AAAA-MM-JJ HH:MM): ")
    end_date = input("Fin (AAAA-MM-JJ HH:MM): ")

    try:
        debut = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        fin = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        if fin <= debut:
            print("[red]La date de fin doit être après la date de début.[/red]")
            conn.close()
            return
    except ValueError:
        print("[red]Format de date invalide.[/red]")
        conn.close()
        return

    location = input("Lieu: ")
    attendees = int(input("Nombre de participants: "))
    notes = input("Notes: ")

    cursor.execute("""
        INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)""", (contract_id, support_id, start_date, end_date, location, attendees, notes))

    conn.commit()
    print("[green]Événement ajouté avec succès ![/green]")
    conn.close()

def filtrer_evenements():
    conn = connect_db()
    cursor = conn.cursor()
    print("=== Filtrer les événements ===")
    filtre = input("Date minimale (AAAA-MM-JJ): ")

    try:
        datetime.strptime(filtre, "%Y-%m-%d")
    except ValueError:
        print("[red]Date invalide.[/red]")
        return

    cursor.execute("SELECT * FROM event WHERE start_date >= ?", (filtre,))
    events = cursor.fetchall()

    if not events:
        print("[yellow]Aucun événement trouvé pour cette date.[/yellow]")
    else:
        table = Table(title="Événements")
        table.add_column("ID")
        table.add_column("Contrat")
        table.add_column("Support")
        table.add_column("Début")
        table.add_column("Fin")
        table.add_column("Lieu")
        table.add_column("Participants")

        for e in events:
            table.add_row(str(e[0]), str(e[1]), str(e[2]), e[3], e[4], e[5], str(e[6]))

        console.print(table)

    conn.close()
