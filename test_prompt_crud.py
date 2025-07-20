import pytest
from unittest.mock import patch, MagicMock
from generic_prompt import prompt_create, prompt_update

# Exemple de champs simulés
client_fields = {
    "full_name": {"type": "str", "prompt": "Nom complet"},
    "email": {"type": "str", "prompt": "Email"},
    "phone": {"type": "str", "prompt": "Téléphone"},
    "company_name": {"type": "str", "prompt": "Entreprise"},
    "created_date": {"type": "date", "prompt": "Date de création (AAAA-MM-JJ)"},
    "last_contact_date": {"type": "date", "prompt": "Dernier contact (AAAA-MM-JJ)"},
    "commercial_id": {"type": "int", "prompt": "ID du commercial"},
}

@pytest.fixture
def mock_field_definitions(monkeypatch):
    monkeypatch.setitem(
        __import__("fields").FIELD_DEFINITIONS,
        "client",
        client_fields
    )

def test_prompt_create_client(mock_field_definitions):
    user_inputs = [
        "Jean Dupont",
        "jean@mail.com",
        "0600000000",
        "Dupont SARL",
        "2024-07-01",
        "2024-07-15",
        "5",
    ]

    with patch("generic_prompt.Prompt.ask", side_effect=user_inputs), \
         patch("generic_prompt.create") as mock_create:

        obj = prompt_create("client")

        assert obj.full_name == "Jean Dupont"
        assert obj.commercial_id == 5
        mock_create.assert_called_once()


def test_prompt_update_client(mock_field_definitions):
    # Objet existant simulé
    existing_client = MagicMock()
    existing_client.id = 1
    existing_client.full_name = "Jean Dupont"
    existing_client.email = "jean@mail.com"
    existing_client.phone = "0600000000"
    existing_client.company_name = "Dupont SARL"
    existing_client.created_date = "2024-07-01"
    existing_client.last_contact_date = "2024-07-15"
    existing_client.commercial_id = 5

    user_inputs = [
        "1",                     # ID à modifier
        "Jean Martin",           # full_name
        "martin@mail.com",       # email
        "0601010101",            # phone
        "Martin SARL",           # company_name
        "2024-08-01",            # created_date
        "2024-08-10",            # last_contact_date
        "6",                     # commercial_id
    ]

    with patch("generic_prompt.get_by_id", return_value=existing_client), \
         patch("generic_prompt.update") as mock_update, \
         patch("generic_prompt.Prompt.ask", side_effect=user_inputs):

        updated_data = prompt_update(user=None, model_name="client")

        assert updated_data["full_name"] == "Jean Martin"
        assert updated_data["commercial_id"] == 6
        mock_update.assert_called_once()
