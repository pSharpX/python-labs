from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductServiceDTO:
    id: int
    code: str
    name: str
    type: str
    smb_applicable: bool
    corp_applicable: bool
    description: Optional[str]
    family_name: str
    line_name: str
