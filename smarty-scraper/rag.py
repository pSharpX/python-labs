import uuid
import chromadb

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from settings import StoreSettings


class IndexingStageRAG:
    def __init__(self, settings: StoreSettings, collection_name: str):
        self.settings = settings
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        # Embedder
        self.embeddings_model = OpenAIEmbeddings()
        # Init vector store
        self.client = chromadb.HttpClient(host=self.settings.host, port=self.settings.port)
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings_model,
            client=self.client,
        )

    @staticmethod
    def __load(resource: str) -> list[Document]:
        loader = WebBaseLoader(resource)
        return loader.load()

    def __chunk(self, docs: list[Document]) -> list[Document]:
        return self.text_splitter.split_documents(docs)

    def pipeline(self, resource):
        docs = IndexingStageRAG.__load(resource)
        chunks = self.__chunk(docs)

        # Insert documents
        ids = [str(uuid.uuid4()) for _ in chunks]
        self.vector_store.add_documents(documents=chunks, ids=ids)
        print("Indexing task completed")


class RetrievalStageRAG:
    def __init__(self, settings: StoreSettings, collection_name: str, top_k: int = 3):
        self.settings = settings
        # Embedder
        self.embeddings_model = OpenAIEmbeddings()
        # Init vector store
        self.client = chromadb.HttpClient(host=self.settings.host, port=self.settings.port)
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings_model,
            client=self.client,
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": top_k})

    def retrieve(self, query: str) -> list[Document]:
        return self.retriever.invoke(input=query)



