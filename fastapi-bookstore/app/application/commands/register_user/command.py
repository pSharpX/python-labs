from dataclasses import dataclass


@dataclass
class RegisterUserCommand:
    email: str
    phone: str
    first_name: str
    last_name: str