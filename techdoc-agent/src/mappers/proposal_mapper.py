from src.domain.proposal_record import ProposalRecord
from src.models.proposal import ProposalModel


class ProposalMapper:
    @staticmethod
    def to_orm(record: ProposalRecord) -> ProposalModel:
        return ProposalModel(
            proposal_id=record.proposal_id,
            owner_id=record.owner_id,
            data=record.model_dump(mode="json"),
            run_state=record.run_state,
            updated_at=record.updated_at,
        )

    @staticmethod
    def to_dto(model: ProposalModel) -> ProposalRecord:
        record = ProposalRecord.model_validate(model.data)
        record.run_state = model.run_state
        return record