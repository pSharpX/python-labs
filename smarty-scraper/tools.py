from typing import Type, Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class SearchProductReviewInput(BaseModel):
    product: str = Field(description="The product to search for")
    query: str = Field(description="query about the product")

class SearchProductReviewTool(BaseTool):
    name: str = "search_product_review"
    description: str = "Search for a product's characteristics, features, or product review"
    args_schema: Type[BaseModel] = SearchProductReviewInput

    _stores: dict = PrivateAttr()

    def __init__(self, stores: dict, **kwargs: Any):
        super().__init__(**kwargs)
        self._stores = stores

    def _run(self, product: str, query: str) -> str:
        """Synchronous execution logic."""
        if product not in self._stores:
            raise ValueError("Invalid product name")

        return self._stores[product].retrieve(query=query)

    async def _arun(self, query: str) -> str:
        """Asynchronous execution logic (optional)."""
        return ""