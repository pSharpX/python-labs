from fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from tools import TechDocDBTools, TechDocGraphRAGTools

mcp = FastMCP(
"TechDoc MCP Server",
    instructions=(
        "Servidor de herramientas y recursos para consultar la arquitectura de catálogo, "
        "tarifas, taxonomías y utilidades del sistema TechDoc."
    ),
)

@mcp.tool(
    name="greet",
    description="Genera un saludo personalizado de bienvenida para verificar la conectividad con el usuario o cliente MCP.",
    tags={"utility", "health"}
)
def greet(
        name: str = Field(description="Nombre de la persona o entidad a saludar.")
) -> str:
    """Devuelve una cadena de texto con un saludo personalizado."""
    return f"Hello, {name}!"

@mcp.tool(
    name="multiply",
    description="Realiza la multiplicación aritmética de dos números decimales o enteros.",
    tags={"utility", "math"}
)
def multiply(
        a: float = Field(description="Primer factor numérico (multiplicando)."),
        b: float = Field(description="Segundo factor numérico (multiplicador).")
) -> float:
    """Calcula y retorna el producto de dos números reales."""
    return a * b

@mcp.resource(
    uri="data://config",
    name="SystemConfiguration",
    description="Proporciona la configuración global y metadatos activos del servidor TechDoc MCP.",
    mime_type="application/json"
)
def get_config() -> dict:
    """Retorna los parámetros de configuración en tiempo de ejecución (tema, versión, etc.)."""
    return {
        "component": "techdoc",
        "theme": "dark",
        "version": "1.0.0",
        "environment": "production"
    }

@mcp.prompt(
    name="analyze_data",
    description="Plantilla predefinida para solicitar un análisis estadístico o descriptivo sobre una serie numérica."
)
def analyze_data(
        data_points: list[float] = Field(description="Lista de valores numéricos a analizar.")
) -> str:
    """Genera el prompt formateado para instruir al modelo a analizar los puntos de datos provistos."""
    formatted_data = ", ".join(str(point) for point in data_points)
    return (
        f"Por favor, analiza la siguiente serie de datos numéricos. "
        f"Identifica patrones, valores atípicos y resumen estadístico: {formatted_data}"
    )

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Endpoint de monitoreo (Liveness/Readiness Probe) para balanceadores de carga"""
    return PlainTextResponse("OK")

if __name__ == "__main__":
    print("="*120)
    print(">> Registering TechDoc Tools")
    print("=" * 120)
    techdoc_db_tools = TechDocDBTools()
    techdoc_graph_tools = TechDocGraphRAGTools()

    mcp.add_tool(techdoc_db_tools.fetch_catalog_by_segment)
    mcp.add_tool(techdoc_db_tools.fetch_catalog_by_product)
    mcp.add_tool(techdoc_db_tools.calculate_tariff)

    mcp.add_tool(techdoc_graph_tools.search_similar_roles)
    mcp.add_tool(techdoc_graph_tools.find_roles_by_category_and_budget)
    mcp.add_tool(techdoc_graph_tools.get_full_taxonomy_context)
    mcp.add_tool(techdoc_graph_tools.get_service_delivery_footprint)

    mcp.run(transport="http")