from typing import Any
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class ModelOutputLogger(BaseCallbackHandler):
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> None:
        generation = response.generations[0][0]

        print("\n" + "=" * 80)
        print("📥 MODEL OUTPUT")
        print("=" * 80)

        print(generation.text)

        print("\n📊 TOKEN USAGE")

        if hasattr(generation, "message"):
            message = generation.message

            print(
                "Input tokens:",
                message.usage_metadata.get("input_tokens")
                if message.usage_metadata
                else None,
            )

            print(
                "Output tokens:",
                message.usage_metadata.get("output_tokens")
                if message.usage_metadata
                else None,
            )

            print(
                "Total tokens:",
                message.usage_metadata.get("total_tokens")
                if message.usage_metadata
                else None,
            )

        print("=" * 80)