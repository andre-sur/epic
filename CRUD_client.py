# client_crud.py
import sqlite3
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

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

def update_client(utilisateur):
    console.print("[bold green]=== Modification d'un client ===[/bold green]")
    client_id = Prompt.ask("ID du client à modifier")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()

    if not client:
        console.print("[red]Client introuvable ou non lié à vous.[/red]")
        conn.close()
        
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
    
def delete_client(utilisateur):
    console.print("[bold red]=== Suppression d'un client ===[/bold red]")
    client_id = Prompt.ask("ID du client à supprimer")

    conn = connect_db()
    cursor = conn.cursor()

    # Récupérer les infos du client pour récapitulatif
    cursor.execute("""
        SELECT id, full_name, email, phone, company_name, created_date, last_contact_date, commercial_id
        FROM client
        WHERE id = ?
    """, (client_id,))
    client = cursor.fetchone()

    if not client:
        console.print("[red]❌ Client introuvable.[/red]")
    else:
        # Afficher récapitulatif
        table = Table(show_header=True, header_style="bold magenta")
        champs = ["ID", "Nom complet", "Email", "Téléphone", "Entreprise", "Date création", "Dernier contact", "ID Commercial"]
        for champ, valeur in zip(champs, [str(c) if c is not None else "" for c in client]):
            table.add_row(champ, valeur)
        console.print(table)

        # Confirmation à la française
        confirmation = Prompt.ask("[bold red]⚠️ Voulez-vous vraiment supprimer ce client ? (o/n)[/bold red]", choices=["o", "n"], default="n")

        if confirmation == "o":
            cursor.execute("DELETE FROM client WHERE id = ?", (client_id,))
            conn.commit()
            console.print("[green]✅ Client supprimé avec succès.[/green]")
        else:
            console.print("[cyan]Suppression annulée.[/cyan]")

    conn.close()
    
def display_clients(utilisateur):
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

def display_all_clients(utilisateur):
    console.print("[bold green]=== Liste de tous les clients ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, email, phone, company_name, created_date, last_contact_date
        FROM client
    """)
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
            table.add_row(
                str(c[0]),
                c[1] or "-",
                c[2] or "-",
                c[3] or "-",
                c[4] or "-",
                c[5] or "-",
                c[6] or "-"
            )

        console.print(table)