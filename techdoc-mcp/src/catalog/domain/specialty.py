from dataclasses import dataclass
from typing import Optional


@dataclass
class SpecialtyDTO:
    code: str
    name: str
    code_example: Optional[str]