from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.table import Table
from fields import FIELD_DEFINITIONS
from generic_dao import *
from models import *
from database import get_connection


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

def prompt_display(model_name):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        console.print(f"[red]Modèle '{model_name}' inconnu.[/red]")
        return
    
    # Récupérer tous les objets
    objects = get_all(table_name=model_name, model_class=model_class)
    fields_to_show = list(FIELD_DEFINITIONS[model_name].keys())

    table = Table(title=f"{model_name.capitalize()}s")
    table.add_column("ID", style="bold yellow")
    for field in fields_to_show:
        table.add_column(field.replace("_", " ").title())
    
    if not objects:
        console.print(f"[yellow]Aucun {model_name} trouvé.[/yellow]")
        return
    
    for obj in objects:
        row = [str(getattr(obj, "id", ""))] + [str(getattr(obj, field, "")) for field in fields_to_show]
        table.add_row(*row)
    
    console.print(table)

def prompt_display_with_filter(model_name):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        console.print(f"[red]Modèle '{model_name}' inconnu.[/red]")
        return

    field_definitions = FIELD_DEFINITIONS.get(model_name)
    if not field_definitions:
        console.print(f"[red]Aucun champ défini pour le modèle '{model_name}'.[/red]")
        return

    available_fields = list(field_definitions.keys())

    console.print(f"\n[bold cyan]Filtrer les {model_name}s :[/bold cyan]")
    for idx, field_name in enumerate(available_fields, start=1):
        label = field_definitions[field_name].get("prompt", field_name)
        console.print(f"[green]{idx}.[/green] {label}")

    # Choix du champ
    while True:
        try:
            choice = int(Prompt.ask("Numéro du champ à utiliser pour filtrer"))
            if 1 <= choice <= len(available_fields):
                filter_field = available_fields[choice - 1]
                break
            else:
                console.print("[red]Numéro invalide.[/red]")
        except ValueError:
            console.print("[red]Veuillez entrer un nombre valide.[/red]")

    # Choix de l'opérateur
    operator = Prompt.ask("Opérateur (par défaut '=')", default="=")

    # Saisie de la valeur
    field_label = field_definitions[filter_field].get("prompt", filter_field)
    filter_value = Prompt.ask(f"Valeur pour : {field_label}")

    # Appel de la fonction d'affichage
    display_with_filter(model_name, filter_field, filter_value, operator)


def display_with_filter(model_name: str, filter_field: str, filter_value, operator: str = "="):
    model_class = MODEL_CLASSES.get(model_name)
    if not model_class:
        console.print(f"[red]Modèle '{model_name}' inconnu.[/red]")
        return

    # Vérifie que le champ est bien défini
    field_definitions = FIELD_DEFINITIONS.get(model_name)
    if not field_definitions or filter_field not in field_definitions:
        console.print(f"[red]Champ '{filter_field}' invalide pour le modèle '{model_name}'.[/red]")
        return

    # Requête filtrée avec opérateur
    objects = get_all_filtered(model_name, model_class, filter_field, filter_value, operator)

    if not objects:
        console.print(f"[yellow]Aucun {model_name} trouvé avec {filter_field} {operator} {filter_value}.[/yellow]")
        return

    # Affichage avec Rich
    available_fields = list(field_definitions.keys())
    table = Table(title=f"{model_name.capitalize()}s filtrés par {filter_field} {operator} {filter_value}")
    table.add_column("ID", style="bold yellow")
    for field in available_fields:
        label = field_definitions[field].get("prompt", field)
        table.add_column(label.title())

    for obj in objects:
        row = [str(getattr(obj, "id", ""))] + [str(getattr(obj, field, "")) for field in available_fields]
        table.add_row(*row)

    console.print(table)
