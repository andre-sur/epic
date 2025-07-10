# cli.py
import click
import sqlite3
from auth import connecter_utilisateur, get_cached_user, save_user_session
from users_CRUD import create_user, update_user, delete_user, display_users
from contract_CRUD import add_contract, update_contract, delete_contract, display_filtered_contracts


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
    """Groupe principal CLI : gère la connexion utilisateur et le contexte."""
    utilisateur = get_cached_user()
    if not utilisateur:
        utilisateur = connecter_utilisateur()
        save_user_session(utilisateur)

    # Stocker dans ctx.obj pour le reste des commandes
    ctx.obj = {
        'user_id': utilisateur['id'],
        'user_name': utilisateur['name'],
        'role': utilisateur['role']
    }


@cli.command(name="creer")
@role_required('gestion')
@click.pass_context
def create(ctx):
    """Créer un utilisateur."""
    create_user()


@cli.command(name="modifier")
@role_required('gestion')
@click.pass_context
def update(ctx):
    """Modifier un utilisateur."""
    update_user()


@cli.command(name="effacer")
@role_required('gestion')
@click.pass_context
def delete(ctx):
    """Supprimer un utilisateur."""
    delete_user()


@cli.command(name="liste")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def list_users(ctx):
    """Afficher la liste des utilisateurs."""
    display_users()

@cli.command(name="ajouter")
@role_required('gestion')
@click.pass_context
def add(ctx):
    """Créer un contrat."""
    add_contract(ctx.obj['utilisateur'])


@cli.command(name="modifier")
@role_required('gestion', 'commercial')
@click.pass_context
def update(ctx):
    """Modifier un contrat."""
    update_contract(ctx.obj['utilisateur'])


@cli.command(name="supprimer")
@role_required('gestion')
@click.pass_context
def delete(ctx):
    """Supprimer un contrat."""
    delete_contract(ctx.obj['utilisateur'])


@cli.command(name="mes")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def my_contracts(ctx):
    """Afficher mes contrats."""
    display_filtered_contracts(ctx.obj['utilisateur'], unpaid=0, unsigned=0)


@cli.command(name="mes-impayes")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def my_unpaid_contracts(ctx):
    """Afficher mes contrats non payés."""
    display_filtered_contracts(ctx.obj['utilisateur'], unpaid=1, unsigned=0)


@cli.command(name="mes-non-signes")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def my_unsigned_contracts(ctx):
    """Afficher mes contrats non signés."""
    display_filtered_contracts(ctx.obj['utilisateur'], unpaid=0, unsigned=1)


@cli.command(name="tous")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def all_contracts(ctx):
    """Afficher tous les contrats."""
    display_filtered_contracts(utilisateur=None, unpaid=0, unsigned=0)


@cli.command(name="tous-impayes")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def all_unpaid_contracts(ctx):
    """Afficher tous les contrats non payés."""
    display_filtered_contracts(utilisateur=None, unpaid=1, unsigned=0)

@cli.command(name="tous-non-signes")
@role_required('gestion', 'commercial', 'support')
@click.pass_context
def all_unsigned_contracts(ctx):
    """Afficher tous les contrats non signés."""
    display_filtered_contracts(utilisateur=None, unpaid=0, unsigned=1)

if __name__ == "__main__":
    cli()
