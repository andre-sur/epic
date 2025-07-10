import sqlite3
import click
from auth import connecter_utilisateur, get_cached_user, save_user_session
import inspect
import sys

DB_PATH = 'epic_crm.db'


def connect_db():
    """Établit une connexion à la base de données SQLite."""
    return sqlite3.connect(DB_PATH)


def role_required(*allowed_roles):
    """Décorateur Click qui restreint l'accès à une commande selon le rôle de l'utilisateur."""
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            user_role = ctx.obj.get('role')
            if user_role not in allowed_roles:
                click.echo(f"⛔️ Accès refusé. Rôle requis : {allowed_roles}")
                ctx.exit()
            return ctx.invoke(f, *args, **kwargs)
        return wrapper
    return decorator


@click.group()
@click.pass_context
def cli(ctx):
    """Groupe principal des commandes CLI, gère la connexion utilisateur et le contexte."""
    global _current_user
    utilisateur = get_cached_user()
    if not utilisateur:
        utilisateur = connecter_utilisateur()
    _current_user = utilisateur

    ctx.obj = {'user_id': utilisateur['id'], 'user_name': utilisateur['name']}


@cli.command()
@role_required('commercial')
@click.pass_context
def creer_client(ctx):
    """Créer un client et l'associer au commercial connecté."""
    click.echo("Commande creer_client exécutée.")
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    full_name = click.prompt("Nom complet du client")
    email = click.prompt("Email du client")
    phone = click.prompt("Numéro de téléphone du client", default="", show_default=False)
    company_name = click.prompt("Nom de l'entreprise", default="", show_default=False)
    created_date = click.prompt("Date de création (AAAA-MM-JJ)", default="", show_default=False)
    last_contact_date = click.prompt("Date du dernier contact (AAAA-MM-JJ)", default="", show_default=False)

    try:
        cursor.execute("""
            INSERT INTO client (full_name, email, phone, company_name, created_date, last_contact_date, commercial_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (full_name, email, phone, company_name, created_date, last_contact_date, user_id))
        conn.commit()
        click.echo(f"✅ Client '{full_name}' ajouté avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de l'ajout du client : {e}")
    finally:
        conn.close()


@cli.command()
@role_required('gestion')
@click.pass_context
def modifier_client(ctx):
    """Modifier un client appartenant au commercial connecté."""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    client_id = click.prompt("ID du client à modifier", type=int)

    cursor.execute("SELECT full_name, email FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    client = cursor.fetchone()
    if not client:
        click.echo("❌ Ce client n'existe pas ou ne vous appartient pas.")
        conn.close()
        return

    click.echo(f"Modification du client : {client[0]} (Email actuel : {client[1]})")
    new_full_name = click.prompt("Nouveau nom complet (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_email = click.prompt("Nouvel email (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_phone = click.prompt("Nouveau téléphone (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_company_name = click.prompt("Nouveau nom entreprise (laisser vide pour ne pas modifier)", default="", show_default=False)
    new_last_contact_date = click.prompt("Nouvelle date dernier contact (AAAA-MM-JJ, vide pour ne pas modifier)", default="", show_default=False)

    try:
        if new_full_name:
            cursor.execute("UPDATE client SET full_name = ? WHERE id = ?", (new_full_name, client_id))
        if new_email:
            cursor.execute("UPDATE client SET email = ? WHERE id = ?", (new_email, client_id))
        if new_phone:
            cursor.execute("UPDATE client SET phone = ? WHERE id = ?", (new_phone, client_id))
        if new_company_name:
            cursor.execute("UPDATE client SET company_name = ? WHERE id = ?", (new_company_name, client_id))
        if new_last_contact_date:
            cursor.execute("UPDATE client SET last_contact_date = ? WHERE id = ?", (new_last_contact_date, client_id))

        conn.commit()
        click.echo("✅ Client modifié avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la modification : {e}")
    finally:
        conn.close()


@cli.command()
@role_required('commercial')
@click.pass_context
def afficher_clients(ctx):
    """Afficher tous les clients associés au commercial connecté."""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, full_name, email, phone, company_name, created_date, last_contact_date 
        FROM client WHERE commercial_id = ?
    """, (user_id,))
    clients = cursor.fetchall()
    conn.close()

    if not clients:
        click.echo("⚠️ Aucun client trouvé.")
        return

    click.echo("=== Liste des clients ===")
    for c in clients:
        click.echo(f"ID: {c[0]}, Nom: {c[1]}, Email: {c[2]}, Téléphone: {c[3]}, Entreprise: {c[4]}, Créé: {c[5]}, Dernier contact: {c[6]}")


@cli.command()
@click.pass_context
def creer_contrat(ctx):
    """Créer un contrat pour un client associé au commercial connecté."""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    client_id = click.prompt("ID du client associé au contrat", type=int)

    cursor.execute("SELECT id FROM client WHERE id = ? AND commercial_id = ?", (client_id, user_id))
    if not cursor.fetchone():
        click.echo("❌ Ce client ne vous est pas associé.")
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
        """, (client_id, user_id, total_amount, amount_due, created_date, int(is_signed)))
        conn.commit()
        click.echo("✅ Contrat créé avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la création du contrat : {e}")
    finally:
        conn.close()


@cli.command()
@click.pass_context
def afficher_contrats(ctx):
    """Afficher les contrats liés au commercial connecté."""
    user_id = ctx.obj['user_id']
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, client_id, total_amount, amount_due, is_signed, created_date 
        FROM contract WHERE commercial_id = ?
    """, (user_id,))
    contrats = cursor.fetchall()
    conn.close()

    if not contrats:
        click.echo("⚠️ Aucun contrat trouvé.")
        return

    click.echo("=== Liste des contrats ===")
    for c in contrats:
        signe = "Oui" if c[4] else "Non"
        click.echo(f"ID: {c[0]}, Client ID: {c[1]}, Montant total: {c[2]:.2f} €, Montant dû: {c[3]:.2f} €, Signé: {signe}, Créé le: {c[5]}")


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
    new_role = click.prompt("Nouveau rôle (gestion, commercial, support) (laisser vide pour ne pas modifier)", default="", show_default=False)

    try:
        if new_name:
            cursor.execute("UPDATE user SET name = ? WHERE id = ?", (new_name, user_id))
        if new_email:
            cursor.execute("UPDATE user SET email = ? WHERE id = ?", (new_email, user_id))
        if new_role:
            cursor.execute("UPDATE user SET role = ? WHERE id = ?", (new_role, user_id))
        conn.commit()
        click.echo("✅ Collaborateur modifié avec succès !")
    except sqlite3.IntegrityError as e:
        click.echo(f"❌ Erreur lors de la modification : {e}")
    finally:
        conn.close()


@cli.command()
@click.pass_context
def afficher_collaborateurs(ctx):
    """Afficher tous les collaborateurs."""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, role FROM user")
    users = cursor.fetchall()
    conn.close()

    if not users:
        click.echo("⚠️ Aucun collaborateur trouvé.")
        return

    click.echo("=== Liste des collaborateurs ===")
    for u in users:
        click.echo(f"ID: {u[0]}, Nom: {u[1]}, Email: {u[2]}, Rôle: {u[3]}")

def display_docstrings():
    module_courant = sys.modules[__name__]
    for nom, fonction in inspect.getmembers(module_courant, inspect.isfunction):
        doc = fonction.__doc__ or "Pas de docstring."
        print(f"Fonction : {nom}\nDocstring : {doc}\n{'-'*40}")

if __name__ == "__main__":
    display_docstrings()
    cli()

