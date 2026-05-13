from dataclasses import dataclass

@dataclass
class UserCreated:
    user_id: str
    email: str
    first_name: str
    last_name: str | None
    phone: str