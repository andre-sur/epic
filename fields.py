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
    # "id" est généré automatiquement, donc on ne le demande pas
    "client_id": {"type": "int", "prompt": "ID du client"},
    "commercial_id": {"type": "int", "prompt": "ID du commercial"},
    "total_amount": {"type": "float", "prompt": "Montant total du contrat"},
    "amount_due": {"type": "float", "prompt": "Montant restant dû"},
    "created_date": {"type": "date", "prompt": "Date de création (AAAA-MM-JJ)"},
    "is_signed": {"type": "bool", "prompt": "Le contrat est-il signé ? (oui/non)"},
    },

    "user": {
    # "id" : auto-généré en base
    "name": {"type": "str", "prompt": "Nom d'utilisateur"},  # changé de "username" → "name"
    "email": {"type": "str", "prompt": "Adresse email"},
    "password": {"type": "str", "prompt": "Mot de passe"},
    "role": {
        "type": "str",
        "prompt": "Rôle (gestion, commercial, support)",
        "choices": ["gestion", "commercial", "support"]
    },
    # "token" : optionnel et généralement non saisi manuellement

    "event": {
    # "id": auto
    "contract_id": {"type": "int", "prompt": "ID du contrat"},
    "support_id": {"type": "int", "prompt": "ID du support (optionnel)", "optional": True},
    "start_date": {"type": "date", "prompt": "Date de début (AAAA-MM-JJ)", "optional": True},
    "end_date": {"type": "date", "prompt": "Date de fin (AAAA-MM-JJ)", "optional": True},
    "location": {"type": "str", "prompt": "Lieu", "optional": True},
    "attendees": {"type": "int", "prompt": "Nombre de participants", "optional": True},
    "notes": {"type": "str", "prompt": "Remarques", "optional": True},
},

}
