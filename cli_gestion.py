import sqlite3
import click
from auth import connecter_utilisateur

DB_PATH = 'epic_crm.db'

def connect_db():
    return sqlite3.connect(DB_PATH)

@click.group()
@click.pass_context
def cli(ctx):
    """Interface CLI de gestion avec authentification."""
    utilisateur = connecter_utilisateur()
    if not utilisateur or utilisateur['role'] != 'gestion':
        click.echo("⛔️ Accès refusé. Seuls les gestionnaires peuvent utiliser cette interface.")
        ctx.exit()
    ctx.obj = {'user_id': utilisateur['id'], 'user_name': utilisateur['name']}

@cli.command()
@click.pass_context
def creer_collaborateur(ctx):
    """Créer un collaborateur (utilisateur)."""
    conn = connect_db()
    cursor = conn.cursor()

    name = click.prompt("Nom complet du collaborateur")
    email = click.prompt("Email")
    password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True)
    role = click.prompt("Rôle (gestion, commercial, support)", type=click.Choice(['gestion', 'commercial', 'support']))

    try:
        cursor.execute("""
            INSERT INTO user (name, email, password, role) VALUES (?, ?, ?, ?)
        """, (name, email, password, role))
        conn.commit()
        click.echo(f"✅ Collaborateur '{name}' créé avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la création : {e}")
    finally:
        conn.close()

@cli.command()
@click.pass_context
def modifier_collaborateur(ctx):
    """Modifier un collaborateur existant."""
    conn = connect_db()
    cursor = conn.cursor()

    user_id = click.prompt("ID du collaborateur à modifier", type=int)
    cursor.execute("SELECT name, email, role FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        click.echo("❌ Collaborateur non trouvé.")
        conn.close()
        return

    click.echo(f"Modification de : {user[0]} (email: {user[1]}, rôle: {user[2]})")
    new_name = click.prompt("Nouveau nom complet (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_email = click.prompt("Nouvel email (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_password = click.prompt("Nouveau mot de passe (laisser vide pour ne pas modifier)", hide_input=True, confirmation_prompt=True, default="", show_default=False)
    new_role = click.prompt("Nouveau rôle (gestion, commercial, support, vide pour ne pas modifier)", default="", show_default=False)

    try:
        if new_name:
            cursor.execute("UPDATE user SET name = ? WHERE id = ?", (new_name, user_id))
        if new_email:
            cursor.execute("UPDATE user SET email = ? WHERE id = ?", (new_email, user_id))
        if new_password:
            cursor.execute("UPDATE user SET password = ? WHERE id = ?", (new_password, user_id))
        if new_role in ['gestion', 'commercial', 'support']:
            cursor.execute("UPDATE user SET role = ? WHERE id = ?", (new_role, user_id))

        conn.commit()
        click.echo("✅ Collaborateur modifié avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la modification : {e}")
    finally:
        conn.close()

@cli.command()
@click.pass_context
def supprimer_collaborateur(ctx):
    """Supprimer un collaborateur."""
    conn = connect_db()
    cursor = conn.cursor()

    user_id = click.prompt("ID du collaborateur à supprimer", type=int)
    cursor.execute("SELECT name FROM user WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        click.echo("❌ Collaborateur non trouvé.")
        conn.close()
        return

    confirm = click.confirm(f"Confirmez-vous la suppression de '{user[0]}' ?", default=False)
    if confirm:
        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()
        click.echo("✅ Collaborateur supprimé avec succès !")
    else:
        click.echo("❌ Suppression annulée.")
    conn.close()

@cli.command()
@click.pass_context
def creer_contrat(ctx):
    """Créer un contrat et l'associer à un client."""
    conn = connect_db()
    cursor = conn.cursor()

    client_id = click.prompt("ID du client associé", type=int)
    # Vérifier que le client existe
    cursor.execute("SELECT full_name FROM client WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    if not client:
        click.echo("❌ Client non trouvé.")
        conn.close()
        return

    commercial_id = click.prompt("ID du commercial associé", type=int)
    # Vérifier que le commercial existe et a le rôle commercial
    cursor.execute("SELECT id FROM user WHERE id = ? AND role = 'commercial'", (commercial_id,))
    if not cursor.fetchone():
        click.echo("❌ Commercial non trouvé ou rôle incorrect.")
        conn.close()
        return

    total_amount = click.prompt("Montant total du contrat", type=float)
    amount_due = click.prompt("Montant restant à payer", type=float)
    created_date = click.prompt("Date de création (AAAA-MM-JJ)")
    is_signed = click.prompt("Le contrat est-il signé ? (0 = non, 1 = oui)", type=click.Choice(['0', '1']))

    try:
        cursor.execute("""
            INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (client_id, commercial_id, total_amount, amount_due, created_date, int(is_signed)))
        conn.commit()
        click.echo("✅ Contrat créé avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la création du contrat : {e}")
    finally:
        conn.close()

@cli.command()
@click.pass_context
def modifier_contrat(ctx):
    """Modifier un contrat existant."""
    conn = connect_db()
    cursor = conn.cursor()

    contrat_id = click.prompt("ID du contrat à modifier", type=int)
    cursor.execute("""
        SELECT client_id, commercial_id, total_amount, amount_due, created_date, is_signed
        FROM contract WHERE id = ?
    """, (contrat_id,))
    contrat = cursor.fetchone()
    if not contrat:
        click.echo("❌ Contrat non trouvé.")
        conn.close()
        return

    new_total_amount = click.prompt(f"Nouveau montant total (actuel: {contrat[2]})", default="", show_default=False)
    new_amount_due = click.prompt(f"Nouveau montant dû (actuel: {contrat[3]})", default="", show_default=False)
    new_is_signed = click.prompt(f"Contrat signé ? (actuel: {'Oui' if contrat[5] else 'Non'}, 0 = non, 1 = oui)", default="", show_default=False)

    try:
        if new_total_amount:
            cursor.execute("UPDATE contract SET total_amount = ? WHERE id = ?", (float(new_total_amount), contrat_id))
        if new_amount_due:
            cursor.execute("UPDATE contract SET amount_due = ? WHERE id = ?", (float(new_amount_due), contrat_id))
        if new_is_signed in ['0', '1']:
            cursor.execute("UPDATE contract SET is_signed = ? WHERE id = ?", (int(new_is_signed), contrat_id))

        conn.commit()
        click.echo("✅ Contrat modifié avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la modification : {e}")
    finally:
        conn.close()

@cli.command()
@click.pass_context
def afficher_evenements_non_assignes(ctx):
    """Afficher les événements sans support assigné."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.contract_id, c.full_name, e.start_date, e.end_date, e.location, e.attendees
        FROM event e
        JOIN contract co ON e.contract_id = co.id
        JOIN client c ON co.client_id = c.id
        WHERE e.support_id IS NULL
    """)
    evenements = cursor.fetchall()
    conn.close()

    if not evenements:
        click.echo("⚠️ Aucun événement non assigné trouvé.")
        return

    click.echo("=== Événements sans support assigné ===")
    for e in evenements:
        click.echo(f"ID: {e[0]}, Contrat: {e[1]}, Client: {e[2]}, Début: {e[3]}, Fin: {e[4]}, Lieu: {e[5]}, Participants: {e[6]}")

@cli.command()
@click.pass_context
def modifier_evenement(ctx):
    """Associer un support à un événement."""
    conn = connect_db()
    cursor = conn.cursor()

    event_id = click.prompt("ID de l'événement à modifier", type=int)
    cursor.execute("SELECT id, support_id FROM event WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    if not event:
        click.echo("❌ Événement non trouvé.")
        conn.close()
        return

    support_id = click.prompt("ID du collaborateur support à assigner")
    # Vérifie que le support existe et a le bon rôle
    cursor.execute("SELECT id FROM user WHERE id = ? AND role = 'support'", (support_id,))
    if not cursor.fetchone():
        click.echo("❌ Collaborateur support non trouvé ou rôle incorrect.")
        conn.close()
        return

    try:
        cursor.execute("UPDATE event SET support_id = ? WHERE id = ?", (support_id, event_id))
        conn.commit()
        click.echo("✅ Support assigné à l'événement avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de l'assignation : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cli()
