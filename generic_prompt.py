from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.table import Table
from fields import FIELD_DEFINITIONS
from generic_dao import *
from models import *

console = Console()

MODEL_CLASSES = {
    "client": Client,
    "contract": Contract,
    "event": Event,
    "user": User,
}

def prompt_create(model_name):
    fields = FIELD_DEFINITIONS[model_name]
    data = {}
    for field_name, field_info in fields.items():
        if field_name == "id":
            continue  # ID auto-incrémenté, on ne demande pas

        prompt_text = field_info.get("prompt", f"Entrez {field_name}")
        default = field_info.get("default", None)

        if default:
            value = Prompt.ask(prompt_text, default=default)
        else:
            value = Prompt.ask(prompt_text)

        # Conversion du type
        field_type = field_info.get("type", "str")
        if field_type == "int":
            value = int(value)
        elif field_type == "float":
            value = float(value)

        data[field_name] = value

    # Créer une instance du modèle
    ModelClass = MODEL_CLASSES[model_name]
    obj = ModelClass(**data)

    # Appeler le DAO pour insérer dans la base
    create(
        table_name=model_name,
        obj=obj,
        fields=data.keys()
    )

    return obj



def prompt_update(user, model_name):
    id_objet = Prompt.ask("Quel ID à modifier")

    existing_object = get_by_id(
        table_name=model_name,
        model_class=MODEL_CLASSES[model_name],
        obj_id=id_objet
    )

    if not existing_object:
        print(f"Objet avec ID {id_objet} non trouvé.")
        return None

    fields = FIELD_DEFINITIONS[model_name]
    data = {}
    for field, field_info in fields.items():
        prompt_text = field_info.get("prompt", field.replace('_', ' ').title())
        current = getattr(existing_object, field)
        answer = Prompt.ask(f"{prompt_text} [{current}]", default=str(current))

        field_type = field_info.get("type", "str")
        if field_type == "int":
            answer = int(answer)
        elif field_type == "float":
            answer = float(answer)

        data[field] = answer

    # Mettre à jour les attributs de l'objet existant avec les nouvelles valeurs
    for field, value in data.items():
        setattr(existing_object, field, value)

    # Appeler la fonction update pour enregistrer dans la base
    update(table_name=model_name, obj=existing_object, fields=data.keys())

    return data


def prompt_delete(model_name):
    """Demande l'ID, affiche les infos, demande confirmation, puis supprime si validé."""

    console.print(f"[bold red]=== Suppression de {model_name} ===[/bold red]")

    # 1. Demander l'ID à supprimer
    obj_id = Prompt.ask("Quel ID voulez-vous supprimer ?")

    # 2. Récupérer l'objet depuis la base
    existing_object = get_by_id(
        table_name=model_name,
        model_class=MODEL_CLASSES[model_name],
        obj_id=obj_id
    )

    if not existing_object:
        console.print(f"[yellow]Aucun objet avec l'ID {obj_id} trouvé.[/yellow]")
        return False

    # 3. Affichage de l'objet
    fields = FIELD_DEFINITIONS[model_name]
    table = Table(title=f"{model_name.capitalize()} à supprimer")

    table.add_column("Champ", style="bold cyan")
    table.add_column("Valeur", style="white")

    for field in fields:
        value = getattr(existing_object, field, "")
        table.add_row(field, str(value))

    console.print(table)

    # 4. Confirmation
    if Confirm.ask("[red]Confirmer la suppression ?[/red]", default=False):
        delete(table_name=model_name, obj_id=existing_object.id)
        console.print("[green]Suppression effectuée avec succès.[/green]")
        return True
    else:
        console.print("[yellow]Suppression annulée.[/yellow]")
        return False



def prompt_display(model_name, objects):
    """Affiche une liste d’objets dans un tableau."""
    fields = FIELD_DEFINITIONS[model_name]
    table = Table(title=f"{model_name.capitalize()}s", show_header=True, header_style="bold magenta")

    table.add_column("ID", style="bold yellow")
    for field in fields:
        table.add_column(field.replace("_", " ").title())

    if not objects:
        console.print(f"[yellow]Aucun {model_name} trouvé.[/yellow]")
        return

    for obj in objects:
        row = [str(getattr(obj, "id", ""))] + [str(getattr(obj, field, "")) for field in fields]
        table.add_row(*row)

    console.print(table)
