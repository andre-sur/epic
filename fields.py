# fields.py

FIELD_DEFINITIONS = {
    "client": {
        #"id": {"type": "int", "prompt": "ID"},
        "full_name": {"type": "str", "prompt": "Nom complet"},
        "email": {"type": "str", "prompt": "Email"},
        "phone": {"type": "str", "prompt": "Téléphone"},
        "company_name": {"type": "str", "prompt": "Entreprise"},
        "created_date": {"type": "date", "prompt": "Date de création (AAAA-MM-JJ)"},
        "last_contact_date": {"type": "date", "prompt": "Dernier contact (AAAA-MM-JJ)"},
        "commercial_id": {"type": "int", "prompt": "ID du commercial"},
    },
    "contract": {
        #"id": {"type": "int", "prompt": "ID"},
        "title": {"type": "str", "prompt": "Titre du contrat"},
        "description": {"type": "str", "prompt": "Description"},
        "status": {"type": "str", "prompt": "Statut"},
        "amount": {"type": "float", "prompt": "Montant"},
        "payment_due": {"type": "date", "prompt": "Date limite de paiement (AAAA-MM-JJ)"},
        "client_id": {"type": "int", "prompt": "ID du client"},
        "commercial_id": {"type": "int", "prompt": "ID du commercial"},
    },
    "user": {
        #"id": {"type": "int", "prompt": "ID"},
        "username": {"type": "str", "prompt": "Nom d'utilisateur"},
        "email": {"type": "str", "prompt": "Email"},
        "role": {"type": "str", "prompt": "Rôle"},
        "password": {"type": "str", "prompt": "Mot de passe"},
        "created_at": {"type": "date", "prompt": "Date de création (AAAA-MM-JJ)"},
    },
    "event": {
        #"id": {"type": "int", "prompt": "ID"},
        "title": {"type": "str", "prompt": "Titre de l'événement"},
        "description": {"type": "str", "prompt": "Description"},
        "date": {"type": "date", "prompt": "Date de l'événement (AAAA-MM-JJ)"},
        "client_id": {"type": "int", "prompt": "ID du client"},
        "contract_id": {"type": "int", "prompt": "ID du contrat"},
        "commercial_id": {"type": "int", "prompt": "ID du commercial"},
    },
}
