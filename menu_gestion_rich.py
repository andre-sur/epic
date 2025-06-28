import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

# Connexion à la base de données
def connect_db():
    return sqlite3.connect('epic_crm.db')

# Menu principal pour les gestionnaires
def afficher_menu_gestion(utilisateur):
    while True:
        console.clear()
        console.rule(f"[bold blue]Menu Gestion – Bienvenue {utilisateur['name']}")
        console.print("1. Créer un collaborateur")
        console.print("2. Mettre à jour un collaborateur")
        console.print("3. Afficher tous les collaborateurs")
        console.print("4. Créer un événement")
        console.print("5. Filtrer les événements")
        console.print("6. Retour au menu principal")

        choix = Prompt.ask("Votre choix", choices=["1", "2", "3", "4", "5", "6"])

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

# Fonction pour créer un collaborateur
def creer_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    console.print("[bold green]=== Création d'un collaborateur ===")
    name = input("Nom : ")
    email = input("Email : ")
    password = input("Mot de passe : ")
    role = Prompt.ask("Rôle", choices=["gestion", "commercial", "support"])

    cursor.execute("""
        INSERT INTO user (name, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, role))

    conn.commit()
    console.print("[green]Collaborateur ajouté avec succès.")
    conn.close()

# Fonction pour mettre à jour un collaborateur
def mettre_a_jour_collaborateur():
    conn = connect_db()
    cursor = conn.cursor()

    console.print("[bold cyan]=== Mise à jour d'un collaborateur ===")
    collaborator_id = input("ID du collaborateur à modifier : ")

    cursor.execute("SELECT * FROM user WHERE id = ?", (collaborator_id,))
    user = cursor.fetchone()

    if not user:
        console.print("[red]Aucun collaborateur trouvé avec cet ID.")
        conn.close()
        return

    name = input("Nouveau nom (laisser vide pour ne pas modifier) : ")
    email = input("Nouveau email (laisser vide pour ne pas modifier) : ")

    if name:
        cursor.execute("UPDATE user SET name = ? WHERE id = ?", (name, collaborator_id))
    if email:
        cursor.execute("UPDATE user SET email = ? WHERE id = ?", (email, collaborator_id))

    conn.commit()
    console.print("[green]Collaborateur mis à jour avec succès.")
    conn.close()

# Fonction pour afficher les collaborateurs dans un tableau rich
def afficher_collaborateurs():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, role FROM user")
    users = cursor.fetchall()

    if not users:
        console.print("[yellow]Aucun collaborateur trouvé.")
        conn.close()
        return

    table = Table(title="Collaborateurs Epic Events")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Nom")
    table.add_column("Email", style="magenta")
    table.add_column("Rôle", style="green")

    for user in users:
        table.add_row(str(user[0]), user[1], user[2], user[3])

    console.print(table)
    conn.close()

# Fonction pour créer un événement
def creer_evenement():
    conn = connect_db()
    cursor = conn.cursor()

    console.print("[bold green]=== Création d'un événement ===")
    contract_id = input("ID du contrat : ")
    support_id = input("ID du support responsable : ")
    start_date = input("Date de début (AAAA-MM-JJ HH:MM) : ")
    end_date = input("Date de fin (AAAA-MM-JJ HH:MM) : ")
    location = input("Lieu : ")
    attendees = int(input("Nombre de participants : "))
    notes = input("Notes : ")

    cursor.execute("""
        INSERT INTO event (contract_id, support_id, start_date, end_date, location, attendees, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (contract_id, support_id, start_date, end_date, location, attendees, notes))

    conn.commit()
    console.print("[green]Événement créé avec succès.")
    conn.close()

# Fonction pour filtrer les événements par date
def filtrer_evenements():
    conn = connect_db()
    cursor = conn.cursor()

    console.print("[bold yellow]=== Filtrer les événements par date de début ===")
    date_filtre = input("Date de début minimale (AAAA-MM-JJ) : ")

    cursor.execute("SELECT * FROM event WHERE start_date >= ?", (date_filtre,))
    events = cursor.fetchall()

    if not events:
        console.print("[yellow]Aucun événement trouvé à partir de cette date.")
        conn.close()
        return

    table = Table(title=f"Événements à partir du {date_filtre}")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Contrat ID", justify="right")
    table.add_column("Support ID", justify="right")
    table.add_column("Début", style="green")
    table.add_column("Fin", style="green")
    table.add_column("Lieu")
    table.add_column("Participants", justify="right")
    table.add_column("Notes", style="dim")

    for e in events:
        table.add_row(
            str(e[0]), str(e[1]), str(e[2] or "-"),
            e[3], e[4], e[5], str(e[6]), e[7] or ""
        )

    console.print(table)
    conn.close()
