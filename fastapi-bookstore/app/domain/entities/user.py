from datetime import datetime
from dataclasses import dataclass

@dataclass
class User:
    id: int
    ext_user_id: str| None
    first_name: str
    last_name: str | None
    email: str
    phone: str
    status: str
    created_at: datetime

    def __init__(self, id, ext_user_id: str | None, first_name: str, last_name: str | None, email: str, phone: str, status: str, created_at: datetime):
        self.id = id
        self.ext_user_id = ext_user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.status = status
        self.created_at = created_at