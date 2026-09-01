import uuid

from agent import RAGPoweredAgent
from rag import IndexingStageRAG, RetrievalStageRAG
from settings import StoreSettings, BaseModelSettings
from tools import SearchProductReviewTool

store_settings = StoreSettings()
model_settings = BaseModelSettings()

product_1_collection = "Alienware_Gaming_Desktop"
product_2_collection = "msi_Codex_Z2_Gaming_Desktop"

indexing_stage_rag_1 = IndexingStageRAG(settings=store_settings, collection_name=product_1_collection)
indexing_stage_rag_2 = IndexingStageRAG(settings=store_settings, collection_name=product_2_collection)

indexing_stage_rag_1.pipeline("https://www.amazon.com/dp/B0F9MRQ328/ref=sspa_sp_vse_RVP_detail_4?sp_csd=d2lkZ2V0TmFtZT1zcF92c2VfUlZQX2RldGFpbA&th=1")
indexing_stage_rag_2.pipeline("https://www.amazon.com/MSI-Codex-Computadora-escritorio-juegos/dp/B0F15TM77B?th=1")

retrieval_stage_rag_1 = RetrievalStageRAG(settings=store_settings, collection_name=product_1_collection)
retrieval_stage_rag_2 = RetrievalStageRAG(settings=store_settings, collection_name=product_2_collection)

search_product_tool = SearchProductReviewTool(
    stores={
        product_1_collection: retrieval_stage_rag_1,
        product_2_collection: retrieval_stage_rag_2,
    }
)

agent = RAGPoweredAgent(
    model_settings=model_settings,
    tools=[ search_product_tool ]
)

if __name__ == '__main__':
    agent.start(
        input_obj={
            "first_product": product_1_collection,
            "second_product": product_2_collection,
            "user_id": str(uuid.uuid4()),
        },
        session_id=str(uuid.uuid4())
    )
