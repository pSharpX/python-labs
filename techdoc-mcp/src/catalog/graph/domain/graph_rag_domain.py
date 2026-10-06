from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TargetSegment(str, Enum):
    """Código de segmento de cliente para la aplicación de tarifas."""

    SMB = "smb"
    CORPORATE = "corporate"


class BusinessLineNode(BaseModel):
    """Representa un nodo de Línea de Negocio en el catálogo."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {"name": "Datos e IA"}
        }
    )

    name: str = Field(
        description="Nombre principal de la línea de negocio dentro de la estructura corporativa.",
        examples=["Datos e IA", "Ciberseguridad", "Cloud & Infraestructura"]
    )


class ProductServiceDTO(BaseModel):
    """Información completa de un producto o servicio del catálogo corporativo."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "business_line": "Datos e IA",
                "family": "Inteligencia Artificial",
                "product_code": "AI-AGT-01",
                "product_name": "Desarrollo de Agentes Virtuales",
                "type": "Implementación",
                "smb_applicable": True,
                "corp_applicable": True,
                "description": "Servicio de diseño e implementación de agentes conversacionales para atención al cliente."
            }
        }
    )

    business_line: str = Field(
        description="Línea de negocio principal a la que pertenece el producto/servicio.",
        examples=["Datos e IA", "Cloud"]
    )
    family: str = Field(
        description="Familia o subcategoría directa del producto dentro de la línea de negocio.",
        examples=["Inteligencia Artificial", "Gobierno de Datos"]
    )
    product_code: str = Field(
        description="Código único e inalterable que identifica al producto/servicio.",
        examples=["AI-AGT-01", "M365-ASS-01"]
    )
    product_name: str = Field(
        description="Nombre comercial o técnico del producto/servicio.",
        examples=["Desarrollo de Agentes Virtuales", "Evaluación de Seguridad Cloud"]
    )
    type: str = Field(
        description="Categoría operativa del servicio (ej. Assessment, Consultoría, Implementación, Soporte).",
        examples=["Assessment", "Implementación", "Migración"]
    )
    smb_applicable: bool = Field(
        description="Indica si el producto/servicio está disponible para el segmento SMB (Pymes)."
    )
    corp_applicable: bool = Field(
        description="Indica si el producto/servicio está disponible para el segmento Corporativo / Enterprise."
    )
    description: Optional[str] = Field(
        default=None,
        description="Descripción detallada del alcance, entregables y capacidades del producto/servicio."
    )


class HourlyRateDTO(BaseModel):
    """Tarifa por hora de un rol profesional según segmento comercial."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "role_code": "HH-DEV",
                "category": "Desarrollo",
                "position": "Desarrollador",
                "level": "Mid",
                "smb_rate": 35.0,
                "corporate_rate": 45.0,
                "description": "Desarrollo y configuración de soluciones de complejidad media."
            }
        }
    )

    role_code: str = Field(
        description="Identificador único del rol profesional en la matriz de tarifas.",
        examples=["HH-DEV-SR", "HH-DEV", "HH-ARQ", "HH-PM", "HH-WEB"]
    )
    category: Optional[str] = Field(
        default=None,
        description="Área o dominio funcional del rol profesional.",
        examples=["Datos", "Gestión de Proyectos", "Arquitectura"]
    )
    position: str = Field(
        description="Título profesional del perfil o puesto de trabajo.",
        examples=["Arquitecto de Datos", "Project Manager", "Consultor AI"]
    )
    level: str = Field(
        description="Nivel de experiencia o seniority del perfil profesional.",
        examples=["Junior", "Mid", "Senior", "Lead"]
    )
    smb_rate: float = Field(
        ge=0,
        description="Costo o tarifa por hora (en USD/moneda local) aplicable a clientes del segmento SMB."
    )
    corporate_rate: float = Field(
        ge=0,
        description="Costo o tarifa por hora (en USD/moneda local) aplicable a clientes del segmento Corporativo."
    )
    description: Optional[str] = Field(
        default=None,
        description="Alcance de responsabilidades, habilidades técnicas y actividades típicas que realiza el rol."
    )


class RoleRequirement(BaseModel):
    """Requerimiento simplificado de un rol y su tarifa asociada para un servicio."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "role": "Consultor Senior AI",
                "rate": 65.0
            }
        }
    )

    role: str = Field(
        description="Nombre o título del rol profesional requerido.",
        examples=["Consultor Senior AI", "Ingeniero Cloud"]
    )
    rate: float = Field(
        ge=0,
        description="Tarifa por hora configurada para este rol en el contexto de entrega del servicio."
    )


class ServiceFootprintDTO(BaseModel):
    """Estructura completa de la huella de entrega (subgrafo) de un producto/servicio."""

    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "product_code": "AI-AGT-01",
                "product_name": "Desarrollo de Agentes Virtuales",
                "product_description": "Diseño e implementación de agentes conversacionales.",
                "family": "Inteligencia Artificial",
                "business_line": "Datos e IA",
                "associated_roles": [
                    {"role": "Arquitecto de IA", "rate": 75.0},
                    {"role": "Desarrollador Python Senior", "rate": 55.0}
                ]
            }
        }
    )

    product_code: str = Field(
        description="Código identificador único del producto evaluado."
    )
    product_name: str = Field(
        description="Nombre comercial del producto o servicio."
    )
    product_description: Optional[str] = Field(
        default=None,
        description="Detalle o resumen del alcance del servicio."
    )
    family: str = Field(
        description="Familia a la que pertenece el producto."
    )
    business_line: str = Field(
        description="Línea de negocio principal a la que está adscrito el servicio."
    )
    associated_roles: List[RoleRequirement] = Field(
        default_factory=list,
        description="Lista de roles profesionales requeridos para la ejecución y entrega del servicio con sus tarifas."
    )
