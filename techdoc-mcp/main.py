from rich import print

from src.catalog.services.tariff_calculation_service import TariffCalculationService
from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.services.product_service_service import CatalogService


def fetch_catalog():
    catalog = CatalogService()
    products: list[ProductServiceDTO] = catalog.fetch_catalog_for_segment("SMB")
    for product in products:
        print(product)

def calculate_tariff():
    # Example query/calculation (Project Manager, Corporate segment, 10 hours, Sunday surcharge)
    tariff_service = TariffCalculationService()
    quote = tariff_service.calculate_service_cost(
        role_code="HH-PM",
        segment="Corporate",
        hours=10,
        surcharge_code="DOM-FER"
    )
    print(f"Role: {quote.position}")
    print(f"Segment: {quote.segment}")
    print(f"Base Rate: ${quote.base_rate}/h")
    print(f"Surcharge Factor: {quote.surcharge_factor}x")
    print(f"Hours: {quote.hours}h")
    print(f"Total Cost: ${quote.total_cost} USD")

def main():
    print("Hello from techdoc-mcp!")
    fetch_catalog()
    calculate_tariff()


if __name__ == "__main__":
    main()
