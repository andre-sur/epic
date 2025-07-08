import os
import sys
import json
import sqlite3
import click
from rich.console import Console
from rich.table import Table
from decorators import require_commercial

console = Console()
SESSION_FILE = '.session'

def connect_db():
    return sqlite3.connect('epic_crm.db')

def get_session():
    if not os.path.exists(SESSION_FILE):
        console.print("[red]❌ Pas de session active, veuillez vous connecter via le menu principal.[/red]")
        sys.exit(1)
    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

def verify_token(user_id, token):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM user WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or row[0] != token:
        console.print("[red]❌ Token invalide ou expiré, veuillez vous reconnecter via le menu principal.[/red]")
        sys.exit(1)

def get_authenticated_user():
    session = get_session()
    user_id = session.get('user_id')
    token = session.get('token')
    verify_token(user_id, token)
    return user_id

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Commandes pour gérer les clients (réservé aux commerciaux)"""
    user_id = get_authenticated_user()
    ctx.obj = {'user_id': user_id}

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@cli.command()
@require_commercial
def display(user_id, role):
    """Afficher vos clients"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, email, company_name FROM client WHERE commercial_id = ?", (user_id,))
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

@cli.command()
@require_commercial
@click.option('--client-id', prompt='ID du client à modifier', type=int)
def update(user_id, role, client_id):
    """Modifier un client (réservé au commercial propriétaire)"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()

    if not client:
        console.print("[red]❌ Client introuvable ou non lié à vous.[/red]")
        conn.close()
        return

    colonnes = [desc[0] for desc in cursor.description]
    client_data = dict(zip(colonnes, client))

    console.print("[bold green]=== Modifier le client ===[/bold green]")
    console.print("Laisser vide pour ne rien changer.")

    champs_modifiables = ['full_name', 'email', 'phone', 'company_name', 'created_date', 'last_contact_date']
    nouvelles_valeurs = {}

    for champ in champs_modifiables:
        valeur_actuelle = client_data.get(champ, '') or ''
        nouvelle_valeur = click.prompt(f"{champ.replace('_', ' ').capitalize()} [{valeur_actuelle}]", default='', show_default=False)
        if nouvelle_valeur != '':
            nouvelles_valeurs[champ] = nouvelle_valeur

    if nouvelles_valeurs:
        set_clause = ", ".join([f"{champ} = ?" for champ in nouvelles_valeurs])
        valeurs = list(nouvelles_valeurs.values()) + [client_id]
        cursor.execute(f"UPDATE client SET {set_clause} WHERE id = ?", valeurs)
        conn.commit()
        console.print("[green]✅ Client modifié avec succès.[/green]")
    else:
        console.print("[yellow]Aucune modification effectuée.[/yellow]")

    conn.close()

@cli.command()
@require_commercial
@click.option('--client-id', prompt='ID du client à supprimer', type=int)
def delete(user_id, role, client_id):
    """Supprimer un client (réservé au commercial propriétaire)"""
    conn = connect_db()
    cursor = conn.cursor()

    console.print("=== Suppression d'un client ===")

    cursor.execute("SELECT id, full_name, email FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()

    if not client:
        console.print("[red]❌ Ce client n'existe pas ou ne vous appartient pas.[/red]")
        conn.close()
        return

    console.print(f"Nom : {client[1]}")
    console.print(f"Email : {client[2]}")

    confirmation = input("⚠️ Êtes-vous sûr de vouloir supprimer ce client ? (o/N): ").strip().lower()

    if confirmation == 'o':
        cursor.execute("DELETE FROM client WHERE id = ?", (client_id,))
        conn.commit()
        console.print("[green]✅ Client supprimé avec succès.[/green]")
    else:
        console.print("[yellow]❌ Suppression annulée.[/yellow]")

    conn.close()

if __name__ == "__main__":
    cli()
