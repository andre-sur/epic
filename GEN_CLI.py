# cli.py
import click
import sqlite3
import json
from auth import connecter_utilisateur, get_cached_user, save_user_session
from CRUD_user import create_user, update_user, delete_user, display_users
from CRUD_event import connect_db, add_event, update_event, delete_event, display_events
from CRUD_client import connect_db, add_client, update_client, delete_client, afficher_clients
from CRUD_contract import add_contract, update_contract, delete_contract, display_filtered_contracts


DB_PATH = 'epic_crm.db'

def connect_db():
    """Établit une connexion à la base de données SQLite."""
    return sqlite3.connect(DB_PATH)


def role_required(*allowed_roles):
    def decorator(f):
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            if ctx.obj is None:
                utilisateur = get_cached_user()
                if not utilisateur:
                    utilisateur = connecter_utilisateur()
                    save_user_session(utilisateur)
                ctx.obj = {
                    'utilisateur': utilisateur,
                    'user_id': utilisateur['id'],
                    'user_name': utilisateur['name'],
                    'role': utilisateur['role']
                }

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

    # Stocker l'objet utilisateur complet dans ctx.obj
""" 
   ctx = {
        'utilisateur': utilisateur,
        'user_id': utilisateur['id'],
        'user_name': utilisateur['name'],
        'role': utilisateur['role']
    }
    """


def create_command(func, roles, name, help_text):
    @cli.command(name=name, help=help_text)
    @role_required(*roles)
    @click.pass_context
    def command(ctx):
        func(ctx)
    return command


# Lecture du fichier JSON de commandes
with open('commands.json', 'r', encoding='utf-8') as f:
    commands = json.load(f)

# Création dynamique des commandes
for cmd in commands:
    func = eval(cmd['func'])  # convertit la chaîne en fonction exécutable
    roles = cmd['roles']
    name = cmd['name']
    help_text = cmd.get('help', '')
    create_command(func, roles, name, help_text)


if __name__ == "__main__":
    cli()
