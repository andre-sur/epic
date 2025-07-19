# client_menu.py
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from DAO_client import (
    add_client,
    get_client_by_id,
    update_client,
    delete_client,
    get_clients_by_commercial,
    get_all_clients
)
from models import Client

console = Console()

def create_client(utilisateur):
    console.print("[bold green]=== Création d'un client ===[/bold green]")
    full_name = Prompt.ask("Nom complet du client")
    email = Prompt.ask("Email")
    phone = Prompt.ask("Téléphone", default="")
    company_name = Prompt.ask("Entreprise", default="")
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)")
    last_contact_date = Prompt.ask("Dernier contact (AAAA-MM-JJ)")

    client = Client(
        id=None,
        full_name=full_name,
        email=email,
        phone=phone,
        company_name=company_name,
        created_date=created_date,
        last_contact_date=last_contact_date,
        commercial_id=utilisateur['id']
    )

    add_client(client)
    console.print("[green]✅ Client créé avec succès.[/green]")

def update_client(utilisateur):
    console.print("[bold green]=== Modification d'un client ===[/bold green]")
    client_id = int(Prompt.ask("ID du client à modifier"))

    client = get_client_by_id(client_id)
    if not client or client.commercial_id != utilisateur['id']:
        console.print("[red]❌ Client introuvable ou non lié à vous.[/red]")
        return

    console.print("[yellow]Laissez vide pour conserver la valeur actuelle.[/yellow]")

    client.full_name = Prompt.ask(f"Nom [{client.full_name}]", default=client.full_name)
    client.email = Prompt.ask(f"Email [{client.email}]", default=client.email)
    client.phone = Prompt.ask(f"Téléphone [{client.phone}]", default=client.phone)
    client.company_name = Prompt.ask(f"Société [{client.company_name}]", default=client.company_name)
    client.created_date = Prompt.ask(f"Création [{client.created_date}]", default=client.created_date)
    client.last_contact_date = Prompt.ask(f"Dernier contact [{client.last_contact_date}]", default=client.last_contact_date)

    update_client(client)
    console.print("[green]✅ Client mis à jour.[/green]")

def delete_client(utilisateur):
    console.print("[bold red]=== Suppression d'un client ===[/bold red]")
    client_id = int(Prompt.ask("ID du client à supprimer"))

    client = get_client_by_id(client_id)
    if not client:
        console.print("[red]❌ Client introuvable.[/red]")
        return

    table = Table(title="Résumé du client")
    for col, val in vars(client).items():
        table.add_row(str(col), str(val))
    console.print(table)

    confirmation = Prompt.ask("Confirmer suppression ? (o/n)", choices=["o", "n"], default="n")
    if confirmation == "o":
        delete_client(client_id)
        console.print("[green]✅ Client supprimé.[/green]")
    else:
        console.print("[cyan]Suppression annulée.[/cyan]")

def list_clients(utilisateur):
    console.print("[bold cyan]=== Vos clients ===[/bold cyan]")
    clients = get_clients_by_commercial(utilisateur['id'])
    _afficher_clients(clients)

def list_all_clients():
    console.print("[bold cyan]=== Tous les clients ===[/bold cyan]")
    clients = get_all_clients()
    _afficher_clients(clients)

def _afficher_clients(clients):
    if not clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Nom")
    table.add_column("Email")
    table.add_column("Téléphone")
    table.add_column("Entreprise")
    table.add_column("Créé le")
    table.add_column("Dernier contact")

    for c in clients:
        table.add_row(
            str(c.id),
            c.full_name,
            c.email or "-",
            c.phone or "-",
            c.company_name or "-",
            c.created_date,
            c.last_contact_date
        )

    console.print(table)
