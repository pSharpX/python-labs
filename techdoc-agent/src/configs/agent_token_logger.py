from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class AgentTokenLogger(BaseCallbackHandler):

    def __init__(self):
        self.iteration = 0

    def on_chat_model_start(
        self,
        serialized,
        messages,
        **kwargs,
    ):
        self.iteration += 1

        print("\n" + "=" * 100)
        print(f"🤖 MODEL ITERATION {self.iteration}")
        print("=" * 100)

        for message in messages[0]:
            print(f"\n[{message.type.upper()}]")
            print(message.content)

    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs,
    ):
        generation = response.generations[0][0]
        message = getattr(generation, "message", None)

        print("\n📥 MODEL OUTPUT")
        print(generation.text)

        if message and message.usage_metadata:
            usage = message.usage_metadata

            print("\n📊 TOKENS")
            print(f"Input:  {usage.get('input_tokens', 0):,}")
            print(f"Output: {usage.get('output_tokens', 0):,}")
            print(f"Total:  {usage.get('total_tokens', 0):,}")

    def on_tool_start(
        self,
        serialized,
        input_str,
        **kwargs,
    ):
        tool_name = serialized.get("name", "unknown")

        print("\n" + "-" * 100)
        print(f"🔧 TOOL START: {tool_name}")
        print("-" * 100)
        print(input_str)

    def on_tool_end(
        self,
        output,
        **kwargs,
    ):
        print("\n🔧 TOOL RESULT")
        print("-" * 100)
        print(output)