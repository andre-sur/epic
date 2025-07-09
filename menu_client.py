import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_client(utilisateur):
    while True:
        console.clear()
        console.rule(f"[bold cyan]Menu Clients – Bienvenue {utilisateur['name']}[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Créer un client")
        table.add_row("2.", "Modifier un client")
        table.add_row("3.", "Supprimer un client")
        table.add_row("4.", "Afficher la liste des clients")
        table.add_row("5.", "[red]Retour au menu précédent[/red]")
        console.print(table)

        choix = Prompt.ask("Veuillez entrer votre choix", choices=["1", "2", "3", "4", "5"])

        if choix == "1":
            if utilisateur['role'] == 'commercial':
                add_client(utilisateur)
            else:
                console.print("[red]Vous n'avez pas la permission de créer un client.[/red]")
                console.input("Appuyez sur Entrée pour continuer...")

        elif choix == "2":
            if utilisateur['role'] == 'commercial':
                update_client(utilisateur)
            else:
                console.print("[red]Vous n'avez pas la permission de modifier un client.[/red]")
                console.input("Appuyez sur Entrée pour continuer...")

        elif choix == "3":
            if utilisateur['role'] == 'gestionnaire':
                delete_client(utilisateur)
            else:
                console.print("[red]Vous n'avez pas la permission de supprimer un client.[/red]")
                console.input("Appuyez sur Entrée pour continuer...")

        elif choix == "4":
            afficher_clients(utilisateur)

        elif choix == "5":
            break

def add_client(utilisateur):
    console.print("[bold green]=== Création d'un client ===[/bold green]")
    full_name = Prompt.ask("Nom complet du client")
    email = Prompt.ask("Email du client")
    phone = Prompt.ask("Téléphone du client (facultatif)", default="")
    company_name = Prompt.ask("Nom de la société (facultatif)", default="")
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    last_contact_date = Prompt.ask("Date du dernier contact (AAAA-MM-JJ)")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, company_name, created_date, last_contact_date, utilisateur['id']))

    conn.commit()
    conn.close()

    console.print("[bold green]✅ Client créé avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def update_client(utilisateur):
    console.print("[bold green]=== Modification d'un client ===[/bold green]")
    client_id = Prompt.ask("ID du client à modifier")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier que le client est lié au commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()

    if not client:
        console.print("[red]Client introuvable ou non lié à vous.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    colonnes = [desc[0] for desc in cursor.description]
    client_data = dict(zip(colonnes, client))

    console.print("[yellow]Laisser vide pour garder la valeur actuelle.[/yellow]")
    new_name = Prompt.ask(f"Nom complet [{client_data['full_name']}]", default=client_data['full_name'])
    new_email = Prompt.ask(f"Email [{client_data['email']}]", default=client_data['email'])
    new_phone = Prompt.ask(f"Téléphone [{client_data['phone']}]", default=client_data['phone'])
    new_company = Prompt.ask(f"Société [{client_data['company_name']}]", default=client_data['company_name'])
    new_created = Prompt.ask(f"Date création [{client_data['created_date']}]", default=client_data['created_date'])
    new_contact = Prompt.ask(f"Dernier contact [{client_data['last_contact_date']}]", default=client_data['last_contact_date'])

    cursor.execute("""
        UPDATE client
        SET full_name = ?, email = ?, phone = ?, company_name = ?, created_date = ?, last_contact_date = ?
        WHERE id = ?
    """, (new_name, new_email, new_phone, new_company, new_created, new_contact, client_id))

    conn.commit()
    conn.close()

    console.print("[green]✅ Client modifié avec succès.[/green]")
    console.input("Appuyez sur Entrée pour continuer...")

def delete_client(utilisateur):
    console.print("[bold red]=== Suppression d'un client ===[/bold red]")
    client_id = Prompt.ask("ID du client à supprimer")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM client WHERE id = ?", (client_id,))
    if not cursor.fetchone():
        console.print("[red]Client introuvable.[/red]")
    else:
        cursor.execute("DELETE FROM client WHERE id = ?", (client_id,))
        conn.commit()
        console.print("[green]✅ Client supprimé avec succès.[/green]")

    conn.close()
    console.input("Appuyez sur Entrée pour continuer...")

def afficher_clients(utilisateur):
    console.print("[bold green]=== Liste des clients ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, email, phone, company_name, created_date, last_contact_date
        FROM client
        WHERE commercial_id = ?
    """, (utilisateur['id'],))
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Nom complet")
        table.add_column("Email")
        table.add_column("Téléphone")
        table.add_column("Société")
        table.add_column("Créé le")
        table.add_column("Dernier contact")

        for c in clients:
            table.add_row(str(c[0]), c[1], c[2], c[3] or "-", c[4] or "-", c[5], c[6])

        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

# Exemple pour tester
if __name__ == "__main__":
    utilisateur_exemple = {"id": 1, "name": "André", "role": "commercial"}
    afficher_menu_client(utilisateur_exemple)
