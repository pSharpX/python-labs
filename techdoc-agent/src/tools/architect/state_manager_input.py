from pydantic import BaseModel, Field


class UpdateTechnicalDocumentInput(BaseModel):
    """Input schema for updating the technical document."""

    technical_document: str = Field(
        description=(
            "Documento técnico-funcional completo generado por el "
            "Arquitecto de Soluciones."
        ),
    )