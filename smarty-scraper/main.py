from agent import RAGPoweredChat
from rag import IndexingStageRAG
from settings import StoreSettings, BaseModelSettings


store_settings = StoreSettings()
model_settings = BaseModelSettings()

indexing_stage_rag = IndexingStageRAG(settings=store_settings)
main_chat = RAGPoweredChat(
    model_settings=model_settings,
    store_settings=store_settings
)

if __name__ == '__main__':
    print("Hello from smarty-scraper!")
    main_chat.initialize()
    #indexing_stage_rag.process("./docs/what_is_llm.txt")
