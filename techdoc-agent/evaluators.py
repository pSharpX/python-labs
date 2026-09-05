import uuid

from deepeval.test_case import LLMTestCase, ToolCall, ToolCallParams
from deepeval.metrics import ToolCorrectnessMetric


class TechDocAgentEvaluator:
    def __init__(self, agent):
        self.agent = agent
        self.metric = ToolCorrectnessMetric(
            threshold=0.8,
            include_reason=True,
            evaluation_params={
                ToolCallParams.INPUT_PARAMETERS
            }
        )

    def run(self, user_input: str, expected_tools: list[ToolCall]):
        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": f"deepeval-{uuid.uuid4()}",
                }
            },
        )

        actual_tools = self._extract_tool_calls(result)
        test_case = LLMTestCase(
            input=user_input,
            actual_output=result["messages"][-1].content,
            tools_called=actual_tools,
            expected_tools=expected_tools,
        )

        self.metric.measure(test_case)
        return {
            "score": self.metric.score,
            "reason": self.metric.reason,
            "tools_called": actual_tools,
        }

    @staticmethod
    def _extract_tool_calls(result) -> list[ToolCall]:
        tools_called = []

        for message in result["messages"]:
            for call in getattr(message, "tool_calls", []):
                tools_called.append(
                    ToolCall(
                        name=call["name"],
                        input_parameters=call.get("args", {}),
                    )
                )

        return tools_called