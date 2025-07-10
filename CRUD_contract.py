import sqlite3
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def connect_db():
    """Établit une connexion à la base de données SQLite."""
    return sqlite3.connect('epic_crm.db')

def add_contract(utilisateur):
    console.print("[bold green]=== Création d'un contrat ===[/bold green]")
    client_id = Prompt.ask("ID du client associé au contrat")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier que le client appartient au commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()

    if not client:
        console.print("[red]Ce client ne vous est pas associé. Vous ne pouvez pas créer de contrat pour lui.[/red]")
        console.input("Appuyez sur Entrée pour continuer...")
        conn.close()
        return

    total_amount = float(Prompt.ask("Montant total du contrat"))
    amount_due = float(Prompt.ask("Montant restant à payer"))
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    is_signed = Prompt.ask("Le contrat est-il signé ? (0 = non, 1 = oui)", choices=["0", "1"])

    cursor.execute("""
        INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, utilisateur['id'], total_amount, amount_due, created_date, int(is_signed)))

    conn.commit()
    conn.close()

    console.print("[bold green]Contrat créé avec succès ![/bold green]")

def update_contract(utilisateur):
    console.print("[bold green]=== Modification d'un contrat ===[/bold green]")
    contrat_id = Prompt.ask("ID du contrat à modifier")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contract WHERE id = ? AND commercial_id = ?", (contrat_id, utilisateur['id']))
    contrat = cursor.fetchone()

    if not contrat:
        console.print("[red]Contrat introuvable ou non lié à vous.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    colonnes = [desc[0] for desc in cursor.description]
    contrat_data = dict(zip(colonnes, contrat))

    console.print("[yellow]Laisser vide pour ne pas modifier.[/yellow]")

    new_total = Prompt.ask(f"Montant total [{contrat_data['total_amount']}]", default=str(contrat_data['total_amount']))
    new_due = Prompt.ask(f"Montant restant à payer [{contrat_data['amount_due']}]", default=str(contrat_data['amount_due']))
    new_date = Prompt.ask(f"Date de création [{contrat_data['created_date']}]", default=contrat_data['created_date'])
    new_signed = Prompt.ask(f"Contrat signé ? (0=non, 1=oui) [{contrat_data['is_signed']}]", choices=["0", "1"], default=str(contrat_data['is_signed']))

    cursor.execute("""
        UPDATE contract
        SET total_amount = ?, amount_due = ?, created_date = ?, is_signed = ?
        WHERE id = ?
    """, (float(new_total), float(new_due), new_date, int(new_signed), contrat_id))

    conn.commit()
    conn.close()

    console.print("[green]✅ Contrat modifié avec succès.[/green]")

def delete_contract(utilisateur):
    console.print("[bold red]=== Suppression d'un contrat ===[/bold red]")
    contrat_id = Prompt.ask("ID du contrat à supprimer")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM contract WHERE id = ?", (contrat_id,))
    if not cursor.fetchone():
        console.print("[red]Contrat introuvable.[/red]")
    else:
        cursor.execute("DELETE FROM contract WHERE id = ?", (contrat_id,))
        conn.commit()
        console.print("[green]✅ Contrat supprimé avec succès.[/green]")

    conn.close()

def display_filtered_contracts(utilisateur, unpaid, unsigned):
    console.print("[bold green]=== Liste des contrats ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()

    # Cas : contrats de l'utilisateur
    if utilisateur and unpaid == 0 and unsigned == 0:
        cursor.execute("""
            SELECT id, client_id, total_amount, amount_due, is_signed
            FROM contract
            WHERE commercial_id = ?
        """, (utilisateur['id'],))

    # Cas : tous les contrats
    elif utilisateur is None and unpaid == 0 and unsigned == 0:
        cursor.execute("""
            SELECT id, client_id, total_amount, amount_due, is_signed
            FROM contract
        """)
        console.print("Tous les contrats")

    # Cas : tous les contrats impayés
    elif utilisateur is None and unpaid == 1:
        cursor.execute("""
            SELECT id, client_id, total_amount, amount_due, is_signed
            FROM contract
            WHERE amount_due > 0
        """)
        console.print("Tous les contrats impayés")

    # Cas : tous les contrats non signés
    elif utilisateur is None and unsigned == 1:
        cursor.execute("""
            SELECT id, client_id, total_amount, amount_due, is_signed
            FROM contract
            WHERE is_signed=0
        """)
        console.print("Tous les contrats non signés")

    # Cas : contrats impayés de l'utilisateur
    elif utilisateur and unpaid == 1:
        cursor.execute("""
            SELECT id, client_id, total_amount, amount_due, is_signed
            FROM contract
            WHERE commercial_id = ? AND amount_due > 0
        """, (utilisateur['id'],))
        console.print(f"Contrats impayés de [bold]{utilisateur['name']}[/bold]")

    # Cas : contrats non signés de l'utilisateur
    elif utilisateur and unsigned == 1:
        cursor.execute("""
            SELECT id, client_id, total_amount, amount_due, is_signed
            FROM contract
            WHERE commercial_id = ? AND is_signed = 0
        """, (utilisateur['id'],))
        console.print(f"Contrats non signés de [bold]{utilisateur['name']}[/bold]")

    contrats = cursor.fetchall()
    conn.close()

    if not contrats:
        console.print("[yellow]Aucun contrat trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Client ID")
        table.add_column("Montant total", justify="right")
        table.add_column("Montant dû", justify="right")
        table.add_column("Signé", justify="center")

        for c in contrats:
            signe = "[green]Oui[/green]" if c[4] else "[red]Non[/red]"
            table.add_row(str(c[0]), str(c[1]), f"{c[2]:.2f} €", f"{c[3]:.2f} €", signe)

        console.print(table)

