from typing import Type, Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from rag import RetrievalStageRAG


class SearchProductReviewInput(BaseModel):
    product: str = Field(description="The product to search for")
    query: str = Field(description="query about the product")

class SearchProductReviewTool(BaseTool):
    name: str = "search_product_review"
    description: str = "Search for a product's characteristics, features, or product review"
    args_schema: Type[BaseModel] = SearchProductReviewInput

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.rag1 = RetrievalStageRAG()
        self.rag2 = RetrievalStageRAG()

    def _run(self, product: str, query: str) -> str:
        """Synchronous execution logic."""
        self.rag1.retrieve(query=query)
        return ""

    async def _arun(self, query: str) -> str:
        """Asynchronous execution logic (optional)."""
        return ""