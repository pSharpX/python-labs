from src.domain.stored_artifact import StoredArtifact
from src.models.artifact import ArtifactModel
from src.shared.enums import ArtifactType


class ArtifactMapper:
    @staticmethod
    def to_orm(artifact: StoredArtifact) -> ArtifactModel:
        return ArtifactModel(
            proposal_id=artifact.proposal_id,
            artifact_type=artifact.artifact_type.value,
            version=artifact.version,
            fingerprint=artifact.fingerprint,
            based_on=artifact.based_on,
            payload=artifact.payload,
            created_at=artifact.created_at,
        )

    @staticmethod
    def to_dto(model: ArtifactModel) -> StoredArtifact:
        return StoredArtifact(
            proposal_id=model.proposal_id,
            artifact_type=ArtifactType(model.artifact_type),
            version=model.version,
            fingerprint=model.fingerprint,
            based_on=model.based_on,
            payload=model.payload,
            created_at=model.created_at,
        )