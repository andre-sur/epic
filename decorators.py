import functools
from rich.console import Console
console = Console()

def require_role(*roles_autorises):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not args:
                console.print("[red]❌ Erreur interne : aucun argument passé au décorateur (ctx manquant).[/red]")
                return
            ctx = args[0]
            role = getattr(ctx, "obj", {}).get('role')
            if role not in roles_autorises:
                console.print(f"[red]❌ Accès refusé : rôle '{role}' non autorisé.[/red]")
                return
            return f(*args, **kwargs)
        return wrapper
    return decorator


