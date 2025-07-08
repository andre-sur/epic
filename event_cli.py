import sqlite3
import json
import click
from rich.console import Console
from rich.table import Table
from decorators import require_support

DB_PATH = 'epic_crm.db'
SESSION_FILE = '.session'
console = Console()


@click.group()
@click.pass_context
def cli(ctx):
    """CLI pour gérer les événements (réservé au support)"""

    # Lire la session sauvegardée
    try:
        with open(SESSION_FILE, 'r') as f:
            session = json.load(f)
            user_id = session.get('user_id')
            token = session.get('token')
    except (FileNotFoundError, json.JSONDecodeError):
        console.print("[red]⛔️ Session non trouvée. Connectez-vous d'abord via le script principal.[/red]")
        ctx.exit(1)

    # Vérifier en BDD que le token est valide
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM user WHERE id = ? AND token = ?", (user_id, token))
    row = cursor.fetchone()
    conn.close()

    if not row:
        console.print("[red]⛔️ Session invalide ou expirée. Veuillez vous reconnecter.[/red]")
        ctx.exit(1)

    ctx.obj = {'user_id': user_id}


@cli.command()
@click.pass_context
@require_support
def list(ctx):
    """Afficher tous les événements attribués au support connecté"""
    user_id = ctx.obj['user_id']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, contract_id, start_date, end_date, location, attendees, notes
        FROM event
        WHERE support_id = ?
    """, (user_id,))
    events = cursor.fetchall()
    conn.close()

    if not events:
        console.print("[yellow]ℹ️ Aucun événement trouvé pour vous.[/yellow]")
        return

    table = Table(title="📅 Événements attribués", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Contrat")
    table.add_column("Début")
    table.add_column("Fin")
    table.add_column("Lieu")
    table.add_column("Participants", justify="right")
    table.add_column("Notes")

    for e in events:
        table.add_row(
            str(e[0]),
            str(e[1]),
            e[2] or "-",
            e[3] or "-",
            e[4] or "-",
            str(e[5]) if e[5] is not None else "-",
            e[6] or "-"
        )

    console.print(table)


@cli.command()
@click.pass_context
@require_support
def edit(ctx):
    """Modifier un événement"""
    event_id = click.prompt("ID de l'événement à modifier", type=int)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, start_date, end_date, location, attendees, notes
        FROM event
        WHERE id = ?
    """, (event_id,))
    event = cursor.fetchone()

    if not event:
        console.print("[red]❌ Événement non trouvé.[/red]")
        conn.close()
        return

    console.print(f"[cyan]Événement actuel:[/cyan] "
                  f"Début={event[1] or '-'}, Fin={event[2] or '-'}, "
                  f"Lieu={event[3] or '-'}, Participants={event[4] or '-'}, Notes={event[5] or '-'}")

    new_start = click.prompt(f"Nouvelle date de début [{event[1] or ''}]", default="", show_default=False)
    new_end = click.prompt(f"Nouvelle date de fin [{event[2] or ''}]", default="", show_default=False)
    new_location = click.prompt(f"Nouveau lieu [{event[3] or ''}]", default="", show_default=False)
    new_attendees = click.prompt(f"Nbre participants [{event[4] if event[4] is not None else ''}]", default="", show_default=False)
    new_notes = click.prompt(f"Nouvelles notes [{event[5] or ''}]", default="", show_default=False)

    updates = []
    values = []

    if new_start:
        updates.append("start_date = ?")
        values.append(new_start)
    if new_end:
        updates.append("end_date = ?")
        values.append(new_end)
    if new_location:
        updates.append("location = ?")
        values.append(new_location)
    if new_attendees:
        try:
            values.append(int(new_attendees))
            updates.append("attendees = ?")
        except ValueError:
            console.print("[red]❌ Nombre de participants invalide.[/red]")
            conn.close()
            return
    if new_notes:
        updates.append("notes = ?")
        values.append(new_notes)

    if updates:
        values.append(event_id)
        query = f"UPDATE event SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        console.print("[green]✅ Événement mis à jour.[/green]")
    else:
        console.print("[yellow]ℹ️ Aucun changement effectué (tout laissé vide).[/yellow]")

    conn.close()


if __name__ == "__main__":
    cli()
