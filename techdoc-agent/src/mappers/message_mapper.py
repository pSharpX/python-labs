from src.domain.stored_message import StoredMessage
from src.models.message import MessageModel


class MessageMapper:
    @staticmethod
    def to_dto(model: MessageModel) -> StoredMessage:
        return StoredMessage(
            id=model.id,
            proposal_id=model.proposal_id,
            role=model.role,
            content=model.content,
            kind=model.kind,
            created_at=model.created_at,
        )