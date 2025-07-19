from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from models import Client  # ta classe Client définie précédemment
from datetime import datetime

console = Console()

# Stockage mémoire simulant la base
clients = []
client_id_counter = 1

def add_client(utilisateur):
    global client_id_counter

    console.print("[bold green]=== Création d'un client ===[/bold green]")
    full_name = Prompt.ask("Nom complet du client")
    email = Prompt.ask("Email du client")
    phone = Prompt.ask("Téléphone du client (facultatif)", default="")
    company_name = Prompt.ask("Nom de la société (facultatif)", default="")
    created_date = Prompt.ask("Date de création (AAAA-MM-JJ)", default=datetime.now().strftime("%Y-%m-%d"))
    last_contact_date = Prompt.ask("Date du dernier contact (AAAA-MM-JJ)", default="")

    # Création de l'objet client
    client = Client(
        id=client_id_counter,
        full_name=full_name,
        email=email,
        phone=phone if phone != "" else None,
        company_name=company_name if company_name != "" else None,
        created_date=created_date,
        last_contact_date=last_contact_date if last_contact_date != "" else None,
        commercial_id=utilisateur['id']
    )
    clients.append(client)
    client_id_counter += 1

    console.print("[bold green]✅ Client créé avec succès ![/bold green]")

def update_client(utilisateur):
    console.print("[bold green]=== Modification d'un client ===[/bold green]")
    client_id = int(Prompt.ask("ID du client à modifier"))

    # Recherche du client appartenant au commercial connecté
    client = next((c for c in clients if c.id == client_id and c.commercial_id == utilisateur['id']), None)

    if not client:
        console.print("[red]Client introuvable ou non lié à vous.[/red]")
        return

    console.print("[yellow]Laisser vide pour garder la valeur actuelle.[/yellow]")

    new_name = Prompt.ask(f"Nom complet [{client.full_name}]", default=client.full_name)
    new_email = Prompt.ask(f"Email [{client.email}]", default=client.email)
    new_phone = Prompt.ask(f"Téléphone [{client.phone or ''}]", default=client.phone or "")
    new_company = Prompt.ask(f"Société [{client.company_name or ''}]", default=client.company_name or "")
    new_created = Prompt.ask(f"Date création [{client.created_date}]", default=client.created_date)
    new_contact = Prompt.ask(f"Dernier contact [{client.last_contact_date or ''}]", default=client.last_contact_date or "")

    # Mise à jour des attributs
    client.full_name = new_name
    client.email = new_email
    client.phone = new_phone if new_phone != "" else None
    client.company_name = new_company if new_company != "" else None
    client.created_date = new_created
    client.last_contact_date = new_contact if new_contact != "" else None

    console.print("[green]✅ Client modifié avec succès.[/green]")

def delete_client(utilisateur):
    console.print("[bold red]=== Suppression d'un client ===[/bold red]")
    client_id = int(Prompt.ask("ID du client à supprimer"))

    client = next((c for c in clients if c.id == client_id), None)

    if not client:
        console.print("[red]❌ Client introuvable.[/red]")
        return

    # Afficher récapitulatif
    table = Table(show_header=True, header_style="bold magenta")
    champs = ["ID", "Nom complet", "Email", "Téléphone", "Entreprise", "Date création", "Dernier contact", "ID Commercial"]
    valeurs = [str(client.id), client.full_name, client.email, client.phone or "-", client.company_name or "-", client.created_date, client.last_contact_date or "-", str(client.commercial_id)]
    for champ, valeur in zip(champs, valeurs):
        table.add_row(champ, valeur)
    console.print(table)

    confirmation = Prompt.ask("[bold red]⚠️ Voulez-vous vraiment supprimer ce client ? (o/n)[/bold red]", choices=["o", "n"], default="n")

    if confirmation == "o":
        clients.remove(client)
        console.print("[green]✅ Client supprimé avec succès.[/green]")
    else:
        console.print("[cyan]Suppression annulée.[/cyan]")

def display_clients(utilisateur):
    console.print("[bold green]=== Liste des clients liés à vous ===[/bold green]")

    filtered_clients = [c for c in clients if c.commercial_id == utilisateur['id']]

    if not filtered_clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Nom complet")
    table.add_column("Email")
    table.add_column("Téléphone")
    table.add_column("Société")
    table.add_column("Créé le")
    table.add_column("Dernier contact")

    for c in filtered_clients:
        table.add_row(
            str(c.id),
            c.full_name,
            c.email,
            c.phone or "-",
            c.company_name or "-",
            c.created_date,
            c.last_contact_date or "-"
        )
    console.print(table)

def display_all_clients(utilisateur):
    console.print("[bold green]=== Liste de tous les clients ===[/bold green]")

    if not clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
        return

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
            str(c.id),
            c.full_name,
            c.email,
            c.phone or "-",
            c.company_name or "-",
            c.created_date,
            c.last_contact_date or "-"
        )

    console.print(table)

