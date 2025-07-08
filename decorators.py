import functools
import click
from db_utils import connect_db

def require_commercial(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        if not ctx.obj or 'user_id' not in ctx.obj:
            click.echo("❌ Utilisateur non connecté dans le contexte.")
            ctx.exit(1)

        user_id = ctx.obj['user_id']

        # Récupérer le rôle depuis la base
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM user WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            click.echo("❌ Utilisateur introuvable.")
            ctx.exit(1)

        role = row[0]

        if role != 'commercial':
            click.echo("❌ Accès refusé : vous devez être un commercial.")
            ctx.exit(1)

        # Passe user_id (et rôle si tu veux) à la fonction décorée
        kwargs['user_id'] = user_id
        kwargs['role'] = role

        return f(*args, **kwargs)

    return wrapper
