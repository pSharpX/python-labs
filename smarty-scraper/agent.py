from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from prompts import SYSTEM_PROMPT
from rag import RetrievalStageRAG
from settings import BaseModelSettings, StoreSettings


class RAGPoweredChat:
    def __init__(self, model_settings: BaseModelSettings, store_settings: StoreSettings):
        self.rag = RetrievalStageRAG(store_settings)
        self.model_settings = model_settings
        self.model = init_chat_model(
            model=self.model_settings.model_name,
            model_provider=self.model_settings.provider,
            temperature=self.model_settings.temperature,
            max_tokens=self.model_settings.max_tokens,
        )
        self.prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    def __ask(self, question: str):
        docs = self.rag.retrieve(question)
        prompt = self.prompt.invoke({"context": docs, "question": question})
        answer = self.model.invoke(prompt)
        return answer

    def initialize(self):
        print("Ask your question: ")
        question = input()
        answer = self.__ask(question)
        print(answer)

