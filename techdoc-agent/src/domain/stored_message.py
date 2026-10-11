from datetime import datetime

from pydantic import BaseModel


class StoredMessage(BaseModel):
    id: int
    proposal_id: str
    role: str
    content: str
    kind: str = "chat"
    created_at: datetime