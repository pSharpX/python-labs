from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SegmentationCriterionDTO:
    id: int = field(
        metadata={"description": "ID único identificador del criterio de segmentación."}
    )
    criterion: str = field(
        metadata={"description": "Nombre o concepto del criterio de segmentación."}
    )
    smb_description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción del criterio aplicable al segmento PyME / SMB."}
    )
    corporate_description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción del criterio aplicable al segmento Corporativo."}
    )
