from typing import Any
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage


class ModelInputLogger(BaseCallbackHandler):
    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        **kwargs: Any,
    ) -> None:
        print("\n" + "=" * 80)
        print("🤖 MODEL INPUT")
        print("=" * 80)

        for message in messages[0]:
            print(f"\n[{message.type.upper()}]")
            print(message.content)

        print("=" * 80)