
from langfuse import get_client
from langfuse.langchain import CallbackHandler


# Initialize Langfuse client
langfuse = get_client()

langfuse_handler = CallbackHandler()
