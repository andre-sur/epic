import os
import sys
import json
import sqlite3
import click
from rich.console import Console
from rich.table import Table
from decorators import require_role

console = Console()
SESSION_FILE = '.session'

def connect_db():
    return sqlite3.connect('epic_crm.db')

def get_session():
    if not os.path.exists(SESSION_FILE):
        console.print("[red]❌ Pas de session active, veuillez vous connecter.[/red]")
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
        console.print("[red]❌ Token invalide ou expiré, veuillez vous reconnecter.[/red]")
        sys.exit(1)

@click.group()
@click.pass_context
def cli(ctx):
    """Commandes pour gérer les clients"""
    session = get_session()
    user_id = session.get('user_id')
    role = session.get('role')
    token = session.get('token')
    verify_token(user_id, token)
    ctx.obj = {'user_id': user_id, 'role': role}

@cli.command()
@click.pass_context
@require_role('commercial')
def create(ctx):
    """Créer un client (réservé aux commerciaux)"""
    user_id = ctx.obj['user_id']
    console.print("[bold green]=== Création d'un nouveau client ===[/bold green]")

    full_name = click.prompt("Nom complet")
    email = click.prompt("Email")
    phone = click.prompt("Téléphone", default="", show_default=False)
    company_name = click.prompt("Nom de l'entreprise", default="", show_default=False)
    created_date = click.prompt("Date de création (YYYY-MM-DD)", default="", show_default=False)
    last_contact_date = click.prompt("Date dernier contact (YYYY-MM-DD)", default="", show_default=False)

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (full_name, email, phone, company_name, created_date, last_contact_date, user_id))
        conn.commit()
        console.print("[green]✅ Client créé avec succès.[/green]")
    except sqlite3.IntegrityError as e:
        console.print(f"[red]❌ Erreur lors de la création : {e}[/red]")
    finally:
        conn.close()

@cli.command()
@click.option('--client-id', prompt='ID du client à modifier', type=int)
@click.pass_context
@require_role('commercial')
def update(ctx, client_id):
    """Modifier un client (réservé au commercial propriétaire)"""
    user_id = ctx.obj['user_id']
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
    console.print("Appuyez sur [enter] pour conserver la valeur actuelle.")

    champs = ['full_name', 'email', 'phone', 'company_name', 'created_date', 'last_contact_date']
    nouvelles_valeurs = {}

    for champ in champs:
        actuel = client_data.get(champ) or ''
        nv = click.prompt(f"{champ.replace('_', ' ').capitalize()} [{actuel}]", default='', show_default=False)
        if nv != '':
            nouvelles_valeurs[champ] = nv

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
@click.option('--client-id', prompt='ID du client à supprimer', type=int)
@click.pass_context
@require_role('commercial')
def delete(ctx, client_id):
    """Supprimer un client (réservé au commercial propriétaire)"""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, full_name FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()

    if not client:
        console.print("[red]❌ Client introuvable ou non lié à vous.[/red]")
        conn.close()
        return

    confirm = click.confirm(f"⚠️ Confirmez-vous la suppression de '{client[1]}' ?", default=False)
    if confirm:
        cursor.execute("DELETE FROM client WHERE id = ?", (client_id,))
        conn.commit()
        console.print("[green]✅ Client supprimé avec succès.[/green]")
    else:
        console.print("[yellow]❌ Suppression annulée.[/yellow]")

    conn.close()

@cli.command()
@click.pass_context
@require_role('commercial','gestion','support')  # Tous les rôles peuvent afficher
def display(ctx):
    """Afficher tous les clients"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.full_name, c.email, c.company_name, u.name AS commercial_name
        FROM client c
        LEFT JOIN user u ON c.commercial_id = u.id
    """)
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        console.print("[yellow]Aucun client trouvé.[/yellow]")
    else:
        table = Table(title="Liste des clients", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Nom complet")
        table.add_column("Email")
        table.add_column("Entreprise")
        table.add_column("Commercial")

        for c in clients:
            table.add_row(str(c[0]), c[1], c[2], c[3], c[4] or '—')

        console.print(table)

if __name__ == "__main__":
    cli()
