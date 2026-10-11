from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.shared.enums import ArtifactType


class StoredArtifact(BaseModel):
    proposal_id: str
    artifact_type: ArtifactType
    version: int
    fingerprint: str
    based_on: dict[str, str] = Field(default_factory=dict)
    payload: dict[str, Any]
    created_at: datetime
