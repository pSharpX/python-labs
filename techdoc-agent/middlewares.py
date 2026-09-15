from typing import Any, override

from deepteam import Guardrails
from deepteam.guardrails import PromptInjectionGuard, ToxicityGuard, HallucinationGuard, CybersecurityGuard, GuardType
from deepteam.guardrails.guards.cybersecurity_guard.cybersecurity_guard import CyberattackCategory
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState, hook_config,
)
from langgraph.runtime import Runtime

from settings import BaseModelSettings


class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"About to call model with {len(state['messages'])} messages")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"Model returned: {state['messages'][-1].content}")
        return None

    async def abefore_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        # Async version of before_model
        return None

    async def aafter_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        # Async version of after_model
        print(f"Model returned: {state['messages'][-1].content}")
        return None


class CustomGuardsMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()
        self.__settings = BaseModelSettings()
        self.__guardrails = Guardrails(
          input_guards=[
              PromptInjectionGuard(),
              CybersecurityGuard(
                  #purpose="API server",
                  categories=[
                      CyberattackCategory.SQL_INJECTION,
                      CyberattackCategory.SHELL_INJECTION,
                      CyberattackCategory.RBAC,
                  ],
                  guard_type=GuardType.INPUT
              )
          ],
          output_guards=[
              ToxicityGuard(),
              HallucinationGuard()
          ]
        )

    @hook_config(can_jump_to=["end"])
    @override
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Check user messages for PromptInjection and Cybersecurity before model invocation.

        Args:
            state: The current agent state.
            runtime: The langgraph runtime.

        Returns:
            Updated state with PII handled according to strategy, or `None` if no attack
                detected.

        Raises:
            PIIDetectionError: If attach is detected and strategy is `'block'`.
        """
        res = self.__guardrails.guard_input(input=state["messages"][-1].content)
        if res.breached:
            pass
        return None

    @hook_config(can_jump_to=["end"])
    @override
    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        res = self.__guardrails.guard_output(input="input", output=state["messages"][-1].content)
        if res.breached:
            pass
        return None

    @override
    async def abefore_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        res = await self.__guardrails.a_guard_input(input=state["messages"][-1].content)
        if res.breached:
            pass
        return None

    @override
    async def aafter_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        res = await self.__guardrails.a_guard_output(input="input", output=state["messages"][-1].content)
        if res.breached:
            pass
        return None

