from typing import List, Optional

from rich import print

from src.catalog.graph.domain.graph_rag_domain import HourlyRateDTO, TargetSegment, ServiceFootprintDTO, ProductServiceDTO as ProductServiceGraphDTO
from src.catalog.graph.services.graph_rag_service import GraphRAGService
from src.catalog.services.tariff_calculation_service import TariffCalculationService
from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.services.product_service_service import CatalogService

x_times = 150

def fetch_catalog():
    catalog = CatalogService()

    print("=" * x_times)
    print("Fetching Catalog")
    print("=" * x_times)

    segment_code = "SMB"
    print(f">> Fetching Catalog by Segment ({segment_code})")

    products: list[ProductServiceDTO] = catalog.fetch_catalog_for_segment(segment_code)
    for product in products:
        print(product)

    product_code = "AI-AGT-01"
    print(f">> Fetching Catalog by Product ({product_code})")
    product: Optional[ProductServiceDTO] = catalog.fetch_product_by_code(product_code)
    print(product)

def calculate_tariff():
    # Example query/calculation (Project Manager, Corporate segment, 10 hours, Sunday surcharge)
    tariff_service = TariffCalculationService()

    print("=" * x_times)
    print("Fetching Tariff")
    print("=" * x_times)

    role_code = "HH-PM"
    segment_code = "Corporate"
    hours = 10
    surcharge_code = "DOM-FER"
    print(f">> Fetching Tariff by Criteria (role_code={role_code}, segment_code={segment_code}, hours={hours}, surcharge_code={surcharge_code})")
    quote = tariff_service.calculate_service_cost(
        role_code=role_code,
        segment=segment_code,
        hours=hours,
        surcharge_code=surcharge_code
    )
    print(f"Role: {quote.position}")
    print(f"Segment: {quote.segment}")
    print(f"Base Rate: ${quote.base_rate}/h")
    print(f"Surcharge Factor: {quote.surcharge_factor}x")
    print(f"Hours: {quote.hours}h")
    print(f"Total Cost: ${quote.total_cost} USD")
    print(quote)

def get_graph_context():
    rag_service = GraphRAGService()

    print("=" * x_times)
    print("Fetching Graph Context")
    print("=" * x_times)
    try:
        print("\n>> 1. Taxonomy Context (Typed Output)")
        products: List[ProductServiceGraphDTO] = rag_service.get_full_taxonomy_context("Datos e IA")
        for p in products:
            print(f"[{p.family}] {p.product_name} ({p.product_code}) -> SMB: {p.smb_applicable}")

        print("\n>> 2. Filtered Hourly Rates (Typed Output)")
        rates: List[HourlyRateDTO] = rag_service.find_roles_by_category_and_budget(
            category="Datos",
            max_rate=45.0,
            target_segment=TargetSegment.CORPORATE
        )
        for r in rates:
            print(f"{r.position} ({r.level}) - Rate: ${r.corporate_rate}/hr")

        print("\n>> 3. Service Footprint Subgraph (JSON output for Prompt Context)")
        footprint: Optional[ServiceFootprintDTO] = rag_service.get_service_delivery_footprint("AI-AGT-01")
        if footprint:
            # Easily serialize to clean JSON for LLM ingestion
            print(footprint.model_dump_json(indent=2))

    finally:
        rag_service.close()

def main():
    print("Hello from techdoc-mcp!")
    fetch_catalog()
    calculate_tariff()
    get_graph_context()


if __name__ == "__main__":
    main()
