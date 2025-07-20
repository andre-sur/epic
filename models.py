from datetime import datetime
from typing import Optional


class User:
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        email: str = "",
        password: str = "",
        role: str = "",
        token: Optional[str] = None,
    ):
        assert role in ("gestion", "commercial", "support"), "Rôle invalide"
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.token = token

    def __repr__(self):
        return f"<User {self.id} | {self.name} ({self.role})>"


class Client:
    def __init__(
        self,
        id: Optional[int] = None,
        full_name: str = "",
        email: str = "",
        phone: Optional[str] = None,
        company_name: Optional[str] = None,
        created_date: Optional[str] = None,
        last_contact_date: Optional[str] = None,
        commercial_id: int = 0,
    ):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.company_name = company_name
        self.created_date = created_date or datetime.now().isoformat()
        self.last_contact_date = last_contact_date
        self.commercial_id = commercial_id

    def __repr__(self):
        return f"<Client {self.id} | {self.full_name}>"


class Contract:
    def __init__(
        self,
        id: Optional[int] = None,
        client_id: int = 0,
        commercial_id: int = 0,
        total_amount: float = 0.0,
        amount_due: float = 0.0,
        created_date: str = "",
        is_signed: bool = False,
    ):
        self.id = id
        self.client_id = client_id
        self.commercial_id = commercial_id
        self.total_amount = total_amount
        self.amount_due = amount_due
        self.created_date = created_date
        self.is_signed = is_signed

    def __repr__(self):
        return f"<Contract {self.id} | Client {self.client_id} | {'Signed' if self.is_signed else 'Pending'}>"


class Event:
    def __init__(
        self,
        id: Optional[int] = None,
        contract_id: int = 0,
        support_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[int] = None,
        notes: Optional[str] = None,
    ):
        self.id = id
        self.contract_id = contract_id
        self.support_id = support_id
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.attendees = attendees
        self.notes = notes

    def __repr__(self):
        return f"<Event {self.id} | Contract {self.contract_id} | {self.location or 'No location'}>"
