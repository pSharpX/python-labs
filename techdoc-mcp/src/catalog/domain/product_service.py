from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductServiceDTO:
    """
    DTO que representa un producto o servicio del catálogo maestro de TechDoc.
    Proporciona información sobre la línea de negocio, familia, aplicabilidad por segmento
    y detalles técnicos del servicio.
    """
    id: int = field(
        metadata={"description": "Identificador único interno del registro en la base de datos."}
    )
    code: str = field(
        metadata={"description": "Código identificador único del servicio (ej. 'M365-ASS-01', 'AZ-MIG-01')."}
    )
    name: str = field(
        metadata={"description": "Nombre oficial del producto o servicio."}
    )
    type: str = field(
        metadata={
            "description": "Modalidad de prestación del servicio (ej. 'Assessment', 'Implementación', 'Migración', 'Seguridad', 'Desarrollo')."}
    )
    smb_applicable: bool = field(
        metadata={
            "description": "Indica si el servicio es aplicable habitualmente para el segmento SMB (hasta 300 usuarios o complejidad estándar)."}
    )
    corp_applicable: bool = field(
        metadata={
            "description": "Indica si el servicio es aplicable para el segmento Corporate (más de 300 usuarios o alta complejidad)."}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Descripción detallada del alcance y objetivo del producto o servicio."}
    )
    family_name: str = field(
        default="",
        metadata={
            "description": "Nombre de la familia tecnológica o funcional a la que pertenece el servicio (ej. 'Microsoft 365', 'Azure', 'Intune')."}
    )
    line_name: str = field(
        default="",
        metadata={
            "description": "Nombre de la línea de negocio principal (ej. 'Modern Work y Microsoft 365', 'Cloud e Infraestructura')."}
    )

    def to_llm_dict(self) -> dict:
        """
        Exporta el DTO en un formato JSON/Dict estructurado optimizado para el contexto de un LLM.
        """
        return {
            "code": self.code,
            "name": self.name,
            "line_name": self.line_name,
            "family_name": self.family_name,
            "type": self.type,
            "smb_applicable": self.smb_applicable,
            "corp_applicable": self.corp_applicable,
            "description": self.description or "Sin descripción disponible."
        }