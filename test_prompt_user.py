import unittest
from unittest.mock import patch
from models import Client, Contract
import generic_prompt

DUMMY_CONTRACT = Contract(
    id=1, client_id=1, commercial_id=2,
    total_amount=1000.0, amount_due=200.0,
    created_date="2025-07-21T10:00:00", is_signed=True
)

DUMMY_CLIENT = Client(
    id=1, full_name="Jean Dupont", email="jean@example.com",
    phone="0123456789", company_name="Entreprise S.A",
    created_date="2025-07-20T10:00:00", last_contact_date=None,
    commercial_id=2
)

class TestGenericPrompt(unittest.TestCase):

    @patch("generic_prompt.Prompt.ask")
    @patch("generic_prompt.create")
    def test_prompt_create_generic_client(self, mock_create, mock_ask):
        mock_ask.side_effect = [
            "Jean Dupont",         # full_name
            "jean@example.com",    # email
            "0123456789",          # phone
            "Entreprise S.A",      # company_name
            "",                    # created_date (laisse vide pour default)
            "",                    # last_contact_date
            "2"                    # commercial_id
        ]

        with patch("generic_prompt.MODEL_CLASSES", {"client": Client}), \
             patch("generic_prompt.FIELD_DEFINITIONS", {
                 "client": {
                     "full_name": {"prompt": "Nom complet"},
                     "email": {"prompt": "Email"},
                     "phone": {"prompt": "Téléphone"},
                     "company_name": {"prompt": "Nom de la société"},
                     "created_date": {"prompt": "Date de création"},
                     "last_contact_date": {"prompt": "Dernier contact"},
                     "commercial_id": {"prompt": "ID Commercial", "type": "int"},
                 }
             }):
            obj = generic_prompt.prompt_create("client")
            self.assertIsInstance(obj, Client)
            self.assertEqual(obj.full_name, "Jean Dupont")
            self.assertEqual(obj.company_name, "Entreprise S.A")
            self.assertEqual(obj.commercial_id, 2)
            mock_create.assert_called_once()

    @patch("generic_prompt.Prompt.ask")
    @patch("generic_prompt.create")
    def test_prompt_create_generic_contract(self, mock_create, mock_ask):
        mock_ask.side_effect = [
            "1",         # client_id
            "2",         # commercial_id
            "1500.5",    # total_amount
            "500.0",     # amount_due
            "",          # created_date
            "True"       # is_signed
        ]

        with patch("generic_prompt.MODEL_CLASSES", {"contract": Contract}), \
             patch("generic_prompt.FIELD_DEFINITIONS", {
                 "contract": {
                     "client_id": {"prompt": "ID Client", "type": "int"},
                     "commercial_id": {"prompt": "ID Commercial", "type": "int"},
                     "total_amount": {"prompt": "Montant total", "type": "float"},
                     "amount_due": {"prompt": "Montant dû", "type": "float"},
                     "created_date": {"prompt": "Date de création"},
                     "is_signed": {"prompt": "Signé", "type": "bool"},
                 }
             }):
            obj = generic_prompt.prompt_create("contract")
            self.assertIsInstance(obj, Contract)
            self.assertEqual(obj.client_id, 1)
            self.assertEqual(obj.total_amount, 1500.5)
            self.assertTrue(obj.is_signed)
            mock_create.assert_called_once()

    @patch("generic_prompt.Prompt.ask")
    @patch("generic_prompt.update")
    @patch("generic_prompt.get_by_id")
    def test_prompt_update_contract(self, mock_get_by_id, mock_update, mock_ask):
        mock_get_by_id.return_value = DUMMY_CONTRACT
        mock_ask.side_effect = [
            "1",         # ID du contrat à modifier
            "1",         # client_id
            "2",         # commercial_id
            "2500.0",    # total_amount
            "1000.0",    # amount_due
            "",          # created_date
            #"False"      # is_signed
        ]

        with patch("generic_prompt.MODEL_CLASSES", {"contract": Contract}), \
             patch("generic_prompt.FIELD_DEFINITIONS", {
                 "contract": {
                     "client_id": {"prompt": "ID Client", "type": "int"},
                     "commercial_id": {"prompt": "ID Commercial", "type": "int"},
                     "total_amount": {"prompt": "Montant total", "type": "float"},
                     "amount_due": {"prompt": "Montant dû", "type": "float"},
                     "created_date": {"prompt": "Date de création"},
                    # "is_signed": {"prompt": "Signé", "type": "bool"},
                 }
             }):
            data = generic_prompt.prompt_update(user=None, model_name="contract")
            self.assertEqual(data["total_amount"], 2500.0)
            self.assertEqual(data["amount_due"], 1000.0)
            #self.assertFalse(data["is_signed"])
            mock_update.assert_called_once()

if __name__ == "__main__":
    unittest.main()
