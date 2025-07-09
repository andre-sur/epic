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
    """Commandes pour gérer les contrats"""
    session = get_session()
    user_id = session.get('user_id')
    role = session.get('role')
    token = session.get('token')
    verify_token(user_id, token)
    ctx.obj = {'user_id': user_id, 'role': role}

@cli.command()
@click.pass_context
@require_role('gestion')
def create(ctx):
    """Créer un contrat (réservé à gestion)"""
    user_id = ctx.obj['user_id']
    console.print("[bold green]=== Création d'un nouveau contrat ===[/bold green]")

    client_id = click.prompt("ID du client", type=int)
    total_amount = click.prompt("Montant total", type=float)
    amount_due = click.prompt("Montant restant dû", type=float)
    created_date = click.prompt("Date de création (YYYY-MM-DD)")
    is_signed = click.confirm("Le contrat est-il signé ?", default=False)

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (client_id, user_id, total_amount, amount_due, created_date, int(is_signed)))
        conn.commit()
        console.print("[green]✅ Contrat créé avec succès.[/green]")
    except sqlite3.IntegrityError as e:
        console.print(f"[red]❌ Erreur lors de la création : {e}[/red]")
    finally:
        conn.close()

@cli.command()
@click.option('--contract-id', prompt='ID du contrat à modifier', type=int)
@click.pass_context
@require_role('gestion')
def update(ctx, contract_id):
    """Modifier un contrat (uniquement gestion)"""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contract WHERE id = ? AND commercial_id = ?", (contract_id, user_id))
    contract = cursor.fetchone()

    if not contract:
        console.print("[red]❌ Contrat introuvable ou non lié à vous.[/red]")
        conn.close()
        return

    colonnes = [desc[0] for desc in cursor.description]
    contract_data = dict(zip(colonnes, contract))

    console.print("[bold green]=== Modifier le contrat ===[/bold green]")
    console.print("Appuyez sur [enter] pour conserver la valeur actuelle.")

    champs = ['client_id', 'total_amount', 'amount_due', 'created_date', 'is_signed']
    nouvelles_valeurs = {}

    for champ in champs:
        actuel = contract_data.get(champ)
        if champ == 'is_signed':
            nv = click.prompt(f"{champ.replace('_', ' ').capitalize()} [{actuel}]", default='', show_default=False)
            if nv != '':
                nouvelles_valeurs[champ] = int(nv)
        else:
            nv = click.prompt(f"{champ.replace('_', ' ').capitalize()} [{actuel}]", default='', show_default=False)
            if nv != '':
                nouvelles_valeurs[champ] = nv

    if nouvelles_valeurs:
        set_clause = ", ".join([f"{champ} = ?" for champ in nouvelles_valeurs])
        valeurs = list(nouvelles_valeurs.values()) + [contract_id]
        cursor.execute(f"UPDATE contract SET {set_clause} WHERE id = ?", valeurs)
        conn.commit()
        console.print("[green]✅ Contrat modifié avec succès.[/green]")
    else:
        console.print("[yellow]Aucune modification effectuée.[/yellow]")

    conn.close()

@cli.command()
@click.option('--contract-id', prompt='ID du contrat à supprimer', type=int)
@click.pass_context
@require_role('gestion')
def delete(ctx, contract_id):
    """Supprimer un contrat (uniquement gestion)"""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM contract WHERE id = ? AND commercial_id = ?", (contract_id, user_id))
    contract = cursor.fetchone()

    if not contract:
        console.print("[red]❌ Contrat introuvable ou non lié à vous.[/red]")
        conn.close()
        return

    confirm = click.confirm(f"⚠️ Confirmez-vous la suppression du contrat ID {contract_id} ?", default=False)
    if confirm:
        cursor.execute("DELETE FROM contract WHERE id = ?", (contract_id,))
        conn.commit()
        console.print("[green]✅ Contrat supprimé avec succès.[/green]")
    else:
        console.print("[yellow]❌ Suppression annulée.[/yellow]")

    conn.close()

@cli.command()
@click.pass_context
@require_role('commercial','gestion','support')
def display(ctx):
    """Afficher tous les contrats"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, cl.full_name AS client_name, u.name AS commercial_name, 
               c.total_amount, c.amount_due, c.created_date, c.is_signed
        FROM contract c
        LEFT JOIN client cl ON c.client_id = cl.id
        LEFT JOIN user u ON c.commercial_id = u.id
    """)
    contracts = cursor.fetchall()
    conn.close()

    if not contracts:
        console.print("[yellow]Aucun contrat trouvé.[/yellow]")
    else:
        table = Table(title="Liste des contrats", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Client")
        table.add_column("Commercial")
        table.add_column("Total")
        table.add_column("Restant dû")
        table.add_column("Date de création")
        table.add_column("Signé")

        for c in contracts:
            table.add_row(
                str(c[0]), c[1] or '—', c[2] or '—',
                f"{c[3]:.2f}", f"{c[4]:.2f}", c[5],
                "Oui" if c[6] else "Non"
            )

        console.print(table)

if __name__ == "__main__":
    cli()
