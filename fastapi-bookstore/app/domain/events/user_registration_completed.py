from dataclasses import dataclass


@dataclass
class UserRegistrationCompleted:
    user_id: str
    email: str
    first_name: str