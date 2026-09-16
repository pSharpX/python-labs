from pydantic import BaseModel, Field

from state import Priority


class SaveMarkdownInput(BaseModel):
    content: str = Field(
        description="Contenido en formato Markdown que se guardará en el archivo."
    )
    filename: str = Field(
        description="Nombre del archivo Markdown que se creará, incluyendo la extensión .md."
    )

class UpdateFunctionalRequirementInput(BaseModel):
    requirement_id: str = Field(
        description="Identificador del requisito funcional."
    )

    description: str = Field(
        description="Descripción actual del requisito funcional."
    )

    priority: Priority = Field(
        description="Prioridad del requisito."
    )

    actor: str | None = Field(
        default=None,
        description="Actor asociado al requisito."
    )

    process: str | None = Field(
        default=None,
        description="Proceso de negocio asociado al requisito."
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="Criterios de aceptación proporcionados o confirmados explícitamente."
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Dependencias conocidas."
    )

    source: str | None = Field(
        default=None,
        description="Fuente del requisito."
    )

    confirmed: bool = Field(
        default=False,
        description="Indica si el requisito ha sido confirmado."
    )