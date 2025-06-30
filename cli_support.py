import sqlite3
import click
from auth import connecter_utilisateur

DB_PATH = 'epic_crm.db'

def connect_db():
    return sqlite3.connect(DB_PATH)

@click.group()
@click.pass_context
def cli(ctx):
    """Interface CLI support avec authentification."""
    utilisateur = connecter_utilisateur()
    if not utilisateur or utilisateur['role'] != 'support':
        click.echo("⛔️ Accès refusé. Seuls les supports peuvent utiliser cette interface.")
        ctx.exit()
    ctx.obj = {'user_id': utilisateur['id'], 'user_name': utilisateur['name']}

@cli.command()
@click.pass_context
def afficher_evenements(ctx):
    """Afficher les événements attribués au support connecté."""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.contract_id, c.full_name, e.start_date, e.end_date, e.location, e.attendees, e.notes
        FROM event e
        JOIN contract co ON e.contract_id = co.id
        JOIN client c ON co.client_id = c.id
        WHERE e.support_id = ?
    """, (user_id,))
    evenements = cursor.fetchall()
    conn.close()

    if not evenements:
        click.echo("⚠️ Aucun événement ne vous est attribué.")
        return

    click.echo("=== Vos événements attribués ===")
    for e in evenements:
        click.echo(f"ID: {e[0]}, Contrat: {e[1]}, Client: {e[2]}, Début: {e[3]}, Fin: {e[4]}, Lieu: {e[5]}, Participants: {e[6]}")
        click.echo(f"Notes: {e[7]}")
        click.echo("-----")

@cli.command()
@click.pass_context
def modifier_evenement(ctx):
    """Modifier un événement dont le support est responsable."""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    event_id = click.prompt("ID de l'événement à modifier", type=int)

    # Vérifie que l'événement appartient bien au support connecté
    cursor.execute("SELECT id FROM event WHERE id = ? AND support_id = ?", (event_id, user_id))
    if not cursor.fetchone():
        click.echo("❌ Événement non trouvé ou vous n'êtes pas responsable de cet événement.")
        conn.close()
        return

    new_start = click.prompt("Nouvelle date/heure de début (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_end = click.prompt("Nouvelle date/heure de fin (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_location = click.prompt("Nouveau lieu (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_attendees = click.prompt("Nouveau nombre de participants (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_notes = click.prompt("Nouvelles notes (laisser vide pour ne pas modifier)", default="", show_default=False)

    try:
        if new_start:
            cursor.execute("UPDATE event SET start_date = ? WHERE id = ?", (new_start, event_id))
        if new_end:
            cursor.execute("UPDATE event SET end_date = ? WHERE id = ?", (new_end, event_id))
        if new_location:
            cursor.execute("UPDATE event SET location = ? WHERE id = ?", (new_location, event_id))
        if new_attendees:
            cursor.execute("UPDATE event SET attendees = ? WHERE id = ?", (int(new_attendees), event_id))
        if new_notes:
            cursor.execute("UPDATE event SET notes = ? WHERE id = ?", (new_notes, event_id))

        conn.commit()
        click.echo("✅ Événement modifié avec succès !")
    except Exception as e:
        click.echo(f"❌ Erreur lors de la modification : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cli()
