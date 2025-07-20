import json
import os
import time
from auth import login, logout, save_user_session, get_cached_user
from token_manager import make_token, clear_token, save_session, clear_session
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import sentry_sdk
from django.http import HttpResponse
from generic_dao import *
from generic_prompt import prompt_create,prompt_update,prompt_delete,prompt_display,prompt_display_with_filter
from fields import FIELD_DEFINITIONS
from models import Client,Contract,User,Event

console = Console()


sentry_sdk.init(
    dsn="https://7f070b8d8417b940e01da3d491c601b8@o4509518763917312.ingest.de.sentry.io/4509518772830288",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,

    traces_sample_rate=1.0,  # pour le monitoring des performances (peut être 0.1 en prod)
    environment="production", ) # ou "development"

def test_sentry_message(request):
    sentry_sdk.capture_message("Message de test depuis Django 🧪")
    return HttpResponse("Message envoyé à Sentry")

DB_PATH = 'epic_crm.db'

# On récupère les données à propos des fonctions et intitulés de menu
def load_commands():
    with open('commands.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    commands = []
    for cmd in data:
        try:
            # Eval pour transformer le texte de func en fonction 
            cmd["func"] = eval(cmd["func"])
            commands.append(cmd)
        except Exception as e:
            console.print(f"[red]Erreur lors du chargement de la commande {cmd['name']} : {e}[/red]")
    return commands

# === Menu principal automatisé selon le rôle
def main_menu(utilisateur):
    commands = load_commands()

    while True:
        console.clear()
        console.rule(f"[bold cyan]📜 Menu des commandes – {utilisateur['name']} ({utilisateur['role']})[/bold cyan]")

        # Filtrer par rôle
        accessible_cmds = [cmd for cmd in commands if utilisateur["role"] in cmd["roles"]]

        # Trier par description (help)
        accessible_cmds.sort(key=lambda c: c["help"])

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("N°", style="cyan")
        table.add_column("Description", style="green")

        for idx, cmd in enumerate(accessible_cmds, start=1):
            table.add_row(str(idx), cmd["help"])

        table.add_row("0", "[red]Déconnecter & Quitter[/red]")

        console.print(table)

        choix = Prompt.ask(
            "Choisissez un numéro",
            choices=[str(i) for i in range(len(accessible_cmds)+1)]
        )

        if choix == "0":
            console.print("[bold red]Au revoir ![/bold red]")
            clear_token(utilisateur['id'])
            clear_session()
            logout()
            print("✅ Token supprimé, utilisateur déconnecté.")
            break
        else:
            idx = int(choix) - 1
            ctx = {"user": utilisateur}  # ctx contient l’utilisateur
            try:
                accessible_cmds[idx]["func"](ctx)
            except Exception as e:
                console.print(f"[red]Erreur lors de l'exécution : {e}[/red]")

        console.input("\n[grey]Appuyez sur Entrée pour continuer...[/grey]")

# === Point d’entrée ===
if __name__ == "__main__":
    utilisateur = get_cached_user()
    # Si pas valide, redemandez
    while not utilisateur:
        utilisateur = login()
        if utilisateur:
            save_user_session(utilisateur)
        else:
            print("⛔️ Connexion échouée, réessayez.\n")

    # générer un token
def start():
    utilisateur = get_cached_user()

    if utilisateur and not is_token_valid(utilisateur.get("token")):
        print("🔐 Token expiré ou invalide. Veuillez vous reconnecter.")
        clear_user_session()
        utilisateur = None

    while not utilisateur:
        email = Prompt.ask("Email")
        password = Prompt.ask("Mot de passe", password=True)
        token = login(email, password)

        if token:
            utilisateur = get_by_field("user", User, "email", email)[0]
            utilisateur_dict = utilisateur.__dict__
            utilisateur_dict["token"] = token
            save_user_session(utilisateur_dict)
        else:
            print("⛔ Connexion échouée. Réessayez.\n")

    main_menu(utilisateur)

if __name__ == "__main__":
    start()