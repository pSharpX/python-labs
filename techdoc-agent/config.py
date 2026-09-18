
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from settings import LangFuseSettings

langfuse_settings = LangFuseSettings()

# Initialize Langfuse client
langfuse = get_client()

langfuse_handler = CallbackHandler()


serde = JsonPlusSerializer(
    allowed_msgpack_modules=[
        ("models", "Actor"),
        ("models", "Process"),
        ("models", "MissingInformation"),
    ]
)