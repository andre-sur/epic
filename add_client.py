# add_client.py

from generic_prompt import prompt_create
from generic_dao import create
from models import Client
from fields import FIELD_DEFINITIONS

def main():
    print("=== Ajout d'un client ===")

    data = prompt_create("client")  # Demande les champs au user
    client = Client(id=None, **data)  # Crée un objet Client

    create("client", client, FIELD_DEFINITIONS["client"])  # Enregistre en base

    print("✅ Client ajouté avec succès.")

if __name__ == "__main__":
    main()
