import logging
from typing import Optional, Literal

from fastmcp.tools import tool

from src.catalog.domain.business_line import BusinessLineDTO
from src.catalog.domain.business_line_role import BusinessLineRoleDTO
from src.catalog.services.business_line_role_service import BusinessLineRoleService
from src.catalog.domain.segmentation_criterion import SegmentationCriterionDTO
from src.catalog.domain.cost_calculation import CostCalculationDTO
from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.graph.domain.graph_rag_domain import HourlyRateDTO, ServiceFootprintDTO, \
    ProductServiceDTO as ProductServiceGraphDTO
from src.catalog.graph.services.graph_rag_service import GraphRAGService
from src.catalog.services.product_service_service import CatalogService
from src.catalog.services.tariff_calculation_service import TariffCalculationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SEGMENT_CODE = Literal["SMB", "CORPORATE"]

class TechDocDBTools:
    def __init__(self):
        self.__catalog_service = CatalogService()
        self.__tariff_service = TariffCalculationService()
        self.__rag_service = GraphRAGService()
        self.__role_service = BusinessLineRoleService()

    @tool(
        name="obtener_criterio_segmentacion",
        description=(
                "Obtiene la lista de todos los criterios de segmentación "
                "comercial y sus descripciones por segmento (SMB/Corporativo)."
        ),
        tags={"segmentation", "search"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def fetch_segmentation_criteria(self) -> list[SegmentationCriterionDTO]:
        """Obtiene la lista completa de criterios de segmentación de la empresa.

        Returns:
            list[SegmentationCriterionDTO]: Lista de DTOs con los criterios y sus descripciones.
        """
        return self.__catalog_service.get_all_criteria()

    @tool(
        name="obtener_lineas_de_negocio",
        description=(
                "Obtiene la lista completa de líneas de negocio disponibles en la organización "
                "junto con sus familias principales de productos/servicios. Utillízala como primer "
                "paso para identificar a qué área o línea pertenece el requerimiento técnico analizado."
        ),
        tags={"catalog", "business_line", "identification"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def fetch_business_lines(self) -> list[BusinessLineDTO]:
        """Obtiene la lista global de líneas de negocio para clasificación de requerimientos.

        Returns:
            list[BusinessLineDTO]: Lista de DTOs con el código, nombre y familias principales de cada línea.
        """
        logger.info(">> Executing tool fetch_business_lines")
        return self.__catalog_service.get_all_business_lines()

    @tool(
        name="obtener_catalogo_por_segmento",
        description=(
            "Busca y retorna la lista de productos y servicios del catálogo "
            "filtrados según el segmento de cliente (ej. SMB o CORPORATE)."
        ),
        tags={"catalog", "search"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def fetch_catalog_by_segment(self, segment_code: SEGMENT_CODE) -> list[ProductServiceDTO]:
        """Obtiene la lista completa de productos y servicios aplicables para un segmento específico.

        Args:
            segment_code (SEGMENT_CODE): Código identificador del segmento comercial.

        Returns:
            list[ProductServiceDTO]: Lista de DTOs con la información de los productos/servicios encontrados.
        """

        logger.info(f">> Fetching Catalog by Segment ({segment_code})")

        products: list[ProductServiceDTO] = self.__catalog_service.fetch_catalog_for_segment(segment_code)
        return products

    @tool(
        name="obtener_catalogo_por_producto",
        description=(
            "Obtiene los detalles específicos de un producto o servicio "
            "del catálogo utilizando su código único (ej. M365-ASS-01)."
        ),
        tags={"catalog", "search"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def fetch_catalog_by_product(self, product_code: str) -> ProductServiceDTO | None:
        """Busca un producto o servicio específico en el catálogo mediante su código de producto.

        Args:
            product_code (str): Código único del producto o servicio a consultar.

        Returns:
            ProductServiceDTO | None: DTO con el detalle del producto/servicio si existe, o None si no se encuentra.
        """

        logger.info(f">> Fetching Catalog by Product ({product_code})")

        product: Optional[ProductServiceDTO] = self.__catalog_service.fetch_product_by_code(product_code)
        return product

    @tool(
        name="obtener_roles_por_linea_de_negocio",
        description=(
                "Consulta los roles principales y de soporte requeridos para una línea "
                "de negocio específica (y opcionalmente por segmento de cliente). Utillízalo "
                "para dimensionar proyectos y preparar estimaciones económicas o propuestas financieras."
        ),
        tags={"catalog", "estimation", "roles"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def fetch_required_roles_by_business_line(
            self, business_line: str, segment: Optional[str] = None
    ) -> list[BusinessLineRoleDTO]:
        """Obtiene la relación de roles principales y secundarios necesarios para dimensionar una línea de negocio.

        Args:
            business_line (str): Nombre o identificador de la línea de negocio a consultar.
            segment (Optional[str]): Segmento objetivo opcional para filtrar los roles (ej. 'SMB', 'CORPORATE').

        Returns:
            list[BusinessLineRoleDTO]: Lista de DTOs con la información de roles principales, de soporte y su descripción de uso.
        """
        logger.info(f">> Executing tool fetch_required_roles_by_business_line ({business_line}, {segment})")
        return self.__role_service.get_roles_by_business_line(
            business_line=business_line, segment=segment
        )

    @tool(
        name="calcular_tarifa",
        description=(
            "Calcula la tarifa o cotización estimada de un servicio "
            "según el rol del especialista, el segmento, las horas estimadas "
            "y posibles recargos."
        ),
        tags={"catalog", "tariff"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def calculate_tariff(self, role_code: str, segment_code: SEGMENT_CODE, hours: int, surcharge_code: str) -> CostCalculationDTO:
        """Calcula el costo total estimado para la prestación de un servicio.

        Args:
            role_code (str): Código del rol técnico o profesional requerido.
            segment_code (SEGMENT_CODE): Código del segmento comercial.
            hours (int): Cantidad de horas estimadas para el servicio.
            surcharge_code (str): Código del recargo o condición tarifaria especial aplicable.

        Returns:
            CostCalculationDTO: Objeto con el desglose del costo y la tarifa final calculada.
        """

        logger.info(f">> Fetching Tariff by Criteria (role_code={role_code}, segment_code={segment_code}, hours={hours}, surcharge_code={surcharge_code})")

        quote: CostCalculationDTO = self.__tariff_service.calculate_service_cost(
            role_code=role_code,
            segment=segment_code,
            hours=hours,
            surcharge_code=surcharge_code
        )
        return quote


class TechDocGraphRAGTools:
    def __init__(self):
        self.__rag_service = GraphRAGService()

    @tool(
        name="obtener_contexto_taxonomia_completa",
        description=(
            "Recupera la jerarquía taxonómica completa (Línea de Negocio -> Familia -> Producto/Servicio) "
            "desde el grafo para una línea de negocio. Útil para entender la oferta comercial y estructura del catálogo."
        ),
        tags={"catalog", "taxonomy", "graphrag"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def get_full_taxonomy_context(self, business_line: str) -> list[ProductServiceGraphDTO]:
        """Consulta y retorna la estructura taxonómica de una línea de negocio en el catálogo."""

        logger.info("Fetching Graph Context")
        logger.info(">> 1. Taxonomy Context (Typed Output)")

        products: list[ProductServiceGraphDTO] = self.__rag_service.get_full_taxonomy_context(business_line)
        return products

    @tool(
        name="buscar_roles_por_categoria_y_presupuesto",
        description=(
            "Filtra roles profesionales y sus tarifas por hora según una categoría funcional (ej. Datos, Cloud), "
            "un tope máximo de tarifa por hora y el segmento comercial del cliente ('smb' o 'corporate')."
        ),
        tags={"catalog", "tariff", "roles", "budget"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def find_roles_by_category_and_budget(self, category: str, max_rate: float | int, segment: SEGMENT_CODE) -> list[HourlyRateDTO]:
        """Filtra y retorna una lista de roles y tarifas por hora según categoría, presupuesto límite y segmento."""

        logger.info("Fetching Graph Context")
        logger.info(">> 2. Filtered Hourly Rates (Typed Output)")

        rates: list[HourlyRateDTO] = self.__rag_service.find_roles_by_category_and_budget(
            category=category,
            max_rate=max_rate,
            target_segment=segment
        )
        return rates

    @tool(
        name="get_service_delivery_footprint",
        description=(
            "Extrae la huella o subgrafo de entrega de un producto/servicio (2 hops), incluyendo su familia, "
            "línea de negocio y los roles/tarifas requeridos para su prestación."
        ),
        tags={"catalog", "service_footprint", "graphrag"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def get_service_delivery_footprint(self, product_code: str) -> ServiceFootprintDTO | None:
        """Extrae el entorno relacional de un producto (taxonomía y roles asociados) serializado en formato JSON."""

        logger.info("Fetching Graph Context")
        logger.info(">> 3. Service Footprint Subgraph (JSON output for Prompt Context)")

        footprint: Optional[ServiceFootprintDTO] = self.__rag_service.get_service_delivery_footprint(product_code)
        if footprint:
            return footprint.model_dump_json(indent=2)
        return None

    @tool(
        name="buscar_roles_similares",
        description=(
            "Realiza una búsqueda textual o por palabras clave en el catálogo de tarifas para encontrar "
            "roles profesionales coincidentes en nombre, nivel, categoría o descripción."
        ),
        tags={"catalog", "roles", "search"},
        meta={"version": "1.0", "author": "techdoc-team"}
    )
    def search_similar_roles(self, query: str) -> list[HourlyRateDTO]:
        """Busca y retorna roles del catálogo que coincidan parcialmente con el término de búsqueda ingresado."""

        logger.info("Fetching Graph Context")
        logger.info(">> 4. Finds matching role nodes (Typed Output)")

        hourly_rates: list[HourlyRateDTO] = self.__rag_service.search_similar_roles(query)
        return hourly_rates