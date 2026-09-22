from langchain_core.tools import tool
from langgraph.types import Command

from .state_manager_input import UpdateTechnicalDocumentInput


@tool("update_technical_document", args_schema=UpdateTechnicalDocumentInput)
def update_technical_document(technical_document: str) -> Command:
    """
    Actualiza el documento técnico-funcional generado por el Arquitecto
    de Soluciones en el estado del workflow.

    Args:
        technical_document: Documento técnico-funcional completo generado
            por el Arquitecto de Soluciones.

    Returns:
        Command que actualiza el campo technical_document del estado.
    """
    if not technical_document or not technical_document.strip():
        raise ValueError(
            "El documento técnico-funcional no puede estar vacío."
        )

    return Command(
        update={
            "technical_document": technical_document.strip()
        }
    )