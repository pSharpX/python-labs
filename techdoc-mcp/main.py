from rich import print

from src.catalog.domain.product_service import ProductServiceDTO
from src.catalog.services.product_service_service import CatalogService


def fetch_catalog():
    catalog = CatalogService()
    products: list[ProductServiceDTO] = catalog.fetch_catalog_for_segment("SMB")
    for product in products:
        print(product)

def main():
    print("Hello from techdoc-mcp!")
    fetch_catalog()


if __name__ == "__main__":
    main()
