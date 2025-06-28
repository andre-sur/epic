import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

console = Console()

def connect_db():
    return sqlite3.connect('epic_crm.db')

def afficher_menu_commercial(utilisateur):
    while True:
        console.clear()
        console.rule(f"[bold cyan]Menu Commercial – Bienvenue {utilisateur['name']}[/bold cyan]")

        table = Table(show_header=False, show_edge=False)
        table.add_row("1.", "Créer un client")
        table.add_row("2.", "Modifier un client")
        table.add_row("3.", "Créer un contrat")
        table.add_row("4.", "Afficher vos clients")
        table.add_row("5.", "Afficher vos contrats")
        table.add_row("6.", "Retour au menu principal")
        console.print(table)

        choix = Prompt.ask("Veuillez entrer votre choix", choices=[str(i) for i in range(1,7)])

        if choix == '1':
            creer_client(utilisateur)
        elif choix == '2':
            modifier_client(utilisateur)
        elif choix == '3':
            creer_contrat(utilisateur)
        elif choix == '4':
            afficher_clients(utilisateur)
        elif choix == '5':
            afficher_contrats(utilisateur)
        elif choix == '6':
            break

def creer_client(utilisateur):
    console.print("[bold green]=== Création d'un client ===[/bold green]")
    full_name = Prompt.ask("Nom complet du client")
    email = Prompt.ask("Email du client")
    phone = Prompt.ask("Numéro de téléphone du client")
    company_name = Prompt.ask("Nom de l'entreprise")
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    last_contact_date = Prompt.ask("Date du dernier contact (AAAA-MM-JJ)")
    commercial_id = utilisateur['id']

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id))
    conn.commit()
    conn.close()

    console.print("[bold green]Client ajouté avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def modifier_client(utilisateur):
    console.print("[bold green]=== Modification d'un client ===[/bold green]")
    client_id = Prompt.ask("ID du client à modifier")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier si client existe
    cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,))
    client_existe = cursor.fetchone()
    if not client_existe:
        console.print("[red]Ce client n'existe pas.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    # Vérifier que le client appartient au commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()
    if not client:
        console.print("[red]Vous n'avez pas la permission de modifier ce client.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    full_name = Prompt.ask("Nouveau nom complet (laisser vide pour ne pas modifier)", default="")
    email = Prompt.ask("Nouvel email (laisser vide pour ne pas modifier)", default="")

    if full_name:
        cursor.execute("UPDATE client SET full_name = ? WHERE id = ?", (full_name, client_id))
    if email:
        cursor.execute("UPDATE client SET email = ? WHERE id = ?", (email, client_id))

    conn.commit()
    conn.close()

    console.print("[bold green]Client modifié avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def creer_contrat(utilisateur):
    console.print("[bold green]=== Création d'un contrat ===[/bold green]")
    client_id = Prompt.ask("ID du client associé au contrat")

    conn = connect_db()
    cursor = conn.cursor()

    # Vérifier que client appartient au commercial
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, utilisateur['id']))
    client = cursor.fetchone()
    if not client:
        console.print("[red]Ce client ne vous est pas associé. Vous ne pouvez pas créer de contrat pour lui.[/red]")
        conn.close()
        console.input("Appuyez sur Entrée pour continuer...")
        return

    commercial_id = utilisateur['id']
    total_amount = float(Prompt.ask("Montant total du contrat"))
    amount_due = float(Prompt.ask("Montant restant à payer"))
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    is_signed = Prompt.ask("Le contrat est-il signé ? (0 = non, 1 = oui)", choices=["0", "1"])

    cursor.execute("""
        INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, commercial_id, total_amount, amount_due, created_date, int(is_signed)))

    conn.commit()
    conn.close()

    console.print("[bold green]Contrat créé avec succès ![/bold green]")
    console.input("Appuyez sur Entrée pour continuer...")

def afficher_clients(utilisateur):
    console.print("[bold green]=== Liste des clients ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, company_name FROM client WHERE commercial_id = ?", (utilisateur['id'],))
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Nom complet")
        table.add_column("Email")
        table.add_column("Entreprise")

        for c in clients:
            table.add_row(str(c[0]), c[1], c[2], c[3])

        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

def afficher_contrats(utilisateur):
    console.print("[bold green]=== Liste des contrats ===[/bold green]")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, client_id, total_amount, amount_due, is_signed FROM contract WHERE commercial_id = ?", (utilisateur['id'],))
    contrats = cursor.fetchall()
    conn.close()

    if not contrats:
        console.print("[yellow]Aucun contrat trouvé.[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Client ID", style="dim", width=10)
        table.add_column("Montant total", justify="right")
        table.add_column("Montant dû", justify="right")
        table.add_column("Signé", justify="center")

        for c in contrats:
            signe = "[green]Oui[/green]" if c[4] else "[red]Non[/red]"
            table.add_row(str(c[0]), str(c[1]), f"{c[2]:.2f} €", f"{c[3]:.2f} €", signe)

        console.print(table)

    console.input("Appuyez sur Entrée pour continuer...")

# Exemple d'appel (à remplacer par l'utilisateur connecté réel)
if __name__ == "__main__":
    utilisateur_exemple = {"id": 1, "name": "André"}
    afficher_menu_commercial(utilisateur_exemple)
