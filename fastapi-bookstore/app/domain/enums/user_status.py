from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CREATED = "CREATED"
    BLOCKED = "BLOCKED"