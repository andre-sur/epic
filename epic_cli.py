import sqlite3
import click
from auth import connecter_utilisateur  # <-- Importation de la fonction d'authentification

def connect_db():
    return sqlite3.connect('epic_crm.db')

@click.group()
@click.pass_context
def cli(ctx):
    """Interface CLI pour le menu commercial (avec authentification)."""
    utilisateur = connecter_utilisateur()
    if not utilisateur:
        click.echo("❌ Authentification échouée. Fin du programme.")
        ctx.exit()
    ctx.ensure_object(dict)
    ctx.obj['user'] = utilisateur

@cli.command()
@click.pass_context
def creer_client(ctx):
    """Créer un client."""
    user_id = ctx.obj['user']['id']
    conn = connect_db()
    cursor = conn.cursor()

    full_name = click.prompt("Nom complet du client")
    email = click.prompt("Email du client")
    phone = click.prompt("Numéro de téléphone du client", default="", show_default=False)
    company_name = click.prompt("Nom de l'entreprise", default="", show_default=False)
    created_date = click.prompt("Date de création (AAAA-MM-JJ)", default="", show_default=False)
    last_contact_date = click.prompt("Date du dernier contact (AAAA-MM-JJ)", default="", show_default=False)

    cursor.execute("""
        INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, company_name, created_date, last_contact_date, user_id))
    conn.commit()
    conn.close()
    click.echo("✅ Client ajouté avec succès !")

@cli.command()
@click.pass_context
def modifier_client(ctx):
    """Modifier un client (appartenant au commercial)."""
    user_id = ctx.obj['user']['id']
    conn = connect_db()
    cursor = conn.cursor()

    client_id = click.prompt("ID du client à modifier", type=int)

    cursor.execute("SELECT * FROM client WHERE id = ?", (client_id,))
    client_existe = cursor.fetchone()
    if not client_existe:
        click.echo("❌ Ce client n'existe pas.")
        conn.close()
        return

    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()
    if not client:
        click.echo("❌ Vous n'avez pas la permission de modifier ce client.")
        conn.close()
        return

    full_name = click.prompt("Nouveau nom complet (laisser vide pour ne pas modifier)", default="", show_default=False)
    email = click.prompt("Nouvel email (laisser vide pour ne pas modifier)", default="", show_default=False)

    if full_name:
        cursor.execute("UPDATE client SET full_name = ? WHERE id = ?", (full_name, client_id))
    if email:
        cursor.execute("UPDATE client SET email = ? WHERE id = ?", (email, client_id))

    conn.commit()
    conn.close()
    click.echo("✅ Client modifié avec succès !")

@cli.command()
@click.pass_context
def creer_contrat(ctx):
    """Créer un contrat pour un client lié au commercial."""
    user_id = ctx.obj['user']['id']
    conn = connect_db()
    cursor = conn.cursor()

    client_id = click.prompt("ID du client associé au contrat", type=int)
    cursor.execute("SELECT * FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()
    if not client:
        click.echo("❌ Ce client ne vous est pas associé. Vous ne pouvez pas créer de contrat pour lui.")
        conn.close()
        return

    total_amount = click.prompt("Montant total du contrat", type=float)
    amount_due = click.prompt("Montant restant à payer", type=float)
    created_date = click.prompt("Date de création (AAAA-MM-JJ)")
    is_signed = click.prompt("Le contrat est-il signé ? (0 = non, 1 = oui)", type=click.Choice(['0','1']), show_choices=True)

    cursor.execute("""
        INSERT INTO contract (client_id, commercial_id, total_amount, amount_due, created_date, is_signed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (client_id, user_id, total_amount, amount_due, created_date, int(is_signed)))

    conn.commit()
    conn.close()
    click.echo("✅ Contrat créé avec succès !")

@cli.command()
@click.pass_context
def afficher_clients(ctx):
    """Afficher les clients liés au commercial."""
    user_id = ctx.obj['user']['id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, full_name, email, company_name FROM client WHERE commercial_id = ?", (user_id,))
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        click.echo("⚠️ Aucun client trouvé.")
        return

    click.echo("=== Liste des clients ===")
    for c in clients:
        click.echo(f"ID: {c[0]}, Nom: {c[1]}, Email: {c[2]}, Entreprise: {c[3]}")

@cli.command()
@click.pass_context
def afficher_contrats(ctx):
    """Afficher les contrats liés au commercial."""
    user_id = ctx.obj['user']['id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, client_id, total_amount, amount_due, is_signed FROM contract WHERE commercial_id = ?", (user_id,))
    contrats = cursor.fetchall()
    conn.close()

    if not contrats:
        click.echo("⚠️ Aucun contrat trouvé.")
        return

    click.echo("=== Liste des contrats ===")
    for c in contrats:
        signe = "Oui" if c[4] else "Non"
        click.echo(f"ID: {c[0]}, Client ID: {c[1]}, Montant total: {c[2]:.2f} €, Montant dû: {c[3]:.2f} €, Signé: {signe}")

if __name__ == "__main__":
    cli()
