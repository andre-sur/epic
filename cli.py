import click
import json
import os
import functools

from generic_dao import create as dao_create, update as dao_update, delete as dao_delete, get_by_id
from models import Client, Contract  # Adapte selon tes modèles
from fields import FIELD_DEFINITIONS
from auth import get_cached_user  # Ta fonction d’auth existante ou stub

SESSION_FILE = "session.json"

MODEL_CLASSES = {
    "client": Client,
    "contract": Contract,
}

# --- Session utils ---

def save_session(user_id, token):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user_id": user_id, "token": token}, f)

def load_session():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# --- Décorateur d’authentification ---

def require_auth(func):
    @functools.wraps(func)
    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        session = load_session()
        if not session or "token" not in session:
            click.echo("❌ Vous devez vous connecter d'abord.")
            ctx.exit(1)
        # Récupérer utilisateur depuis session, tu peux aussi appeler get_cached_user si tu préfères
        utilisateur = {"id": session["user_id"], "token": session["token"]}
        return func(*args, utilisateur=utilisateur, **kwargs)
    return wrapper

# --- CLI Group ---

@click.group()
def cli():
    pass

# --- Login / Logout ---

@cli.command()
@click.option("--user", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login(user, password):
    # Exemple simple, remplace par ta vérif réelle (base, hash, etc)
    if user == "admin" and password == "secret":
        save_session(user_id=1, token="secure-token")
        click.echo("✅ Connecté.")
    else:
        click.echo("❌ Identifiants invalides.")

@cli.command()
def logout():
    clear_session()
    click.echo("🚪 Déconnecté.")

# --- CRUD Commands ---

@cli.command()
@require_auth
@click.argument("model_name")
def create(model_name, utilisateur):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        click.echo("❌ Modèle inconnu.")
        return

    fields = FIELD_DEFINITIONS[model_name]
    data = {}

    for field, info in fields.items():
        if field == "id":
            continue
        prompt = info.get("prompt", field)
        default = info.get("default")
        value = click.prompt(prompt, default=default)
        if info.get("type") == "int":
            value = int(value)
        data[field] = value

    obj = model_class(**data)
    dao_create(model_name, obj, list(data.keys()))
    click.echo("✅ Objet créé avec succès.")

@cli.command()
@require_auth
@click.argument("model_name")
@click.argument("obj_id")
def read(model_name, obj_id, utilisateur):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        click.echo("❌ Modèle inconnu.")
        return

    obj = get_by_id(model_name, model_class, obj_id)
    if not obj:
        click.echo("❌ Objet non trouvé.")
        return

    click.echo(f"📄 {model_name.capitalize()} {obj_id} :")
    for field in FIELD_DEFINITIONS[model_name]:
        click.echo(f"  {field}: {getattr(obj, field)}")

@cli.command()
@require_auth
@click.argument("model_name")
@click.argument("obj_id")
def update(model_name, obj_id, utilisateur):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        click.echo("❌ Modèle inconnu.")
        return

    obj = get_by_id(model_name, model_class, obj_id)
    if not obj:
        click.echo("❌ Objet non trouvé.")
        return

    fields = FIELD_DEFINITIONS[model_name]
    updated_fields = []
    for field, info in fields.items():
        if field == "id":
            continue
        current = getattr(obj, field)
        prompt = info.get("prompt", field)
        value = click.prompt(f"{prompt} (actuel: {current})", default=str(current))
        if info.get("type") == "int":
            value = int(value)
        setattr(obj, field, value)
        updated_fields.append(field)

    dao_update(model_name, obj, updated_fields)
    click.echo("✅ Objet mis à jour.")

@cli.command()
@require_auth
@click.argument("model_name")
@click.argument("obj_id")
def delete(model_name, obj_id, utilisateur):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        click.echo("❌ Modèle inconnu.")
        return

    obj = get_by_id(model_name, model_class, obj_id)
    if not obj:
        click.echo("❌ Objet non trouvé.")
        return

    confirm = click.confirm(f"Supprimer {model_name} {obj_id} ?", default=False)
    if confirm:
        dao_delete(model_name, obj_id)
        click.echo("🗑️ Objet supprimé.")
    else:
        click.echo("❌ Suppression annulée.")

# --- Entrée principale ---

if __name__ == "__main__":
    cli()
