import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import serde
from settings import BaseModelSettings
from src.prompts import FINANCIAL_ESTIMATE_SYSTEM_PROMPT
from src.state.financial_estimator import FinancialEstimatorOutputSchema

tools = [
]

class FinancialEstimatorAgent:
    """
    TODO
    """
    def __init__(self):
        self.__model_settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__model_settings.model_name,
            model_provider=self.__model_settings.provider,
            temperature=self.__model_settings.temperature,
        )
        self.__system_prompt = FINANCIAL_ESTIMATE_SYSTEM_PROMPT
        self.__agent = create_agent(
            model=self.__model,
            tools=tools,
            system_prompt=self.__system_prompt,
            name="financial-estimator-agent",
            response_format=FinancialEstimatorOutputSchema,
            #checkpointer=InMemorySaver(serde=serde)
        )

    def run(self, requirements: dict, technical_proposal: dict, catalog: list[dict]) -> FinancialEstimatorOutputSchema:
        prompt = (
                "Prepare la estimación del esfuerzo utilizando ÚNICAMENTE estos datos de entrada. La aplicación realizará "
                "el cálculo aritmético decimal final.\n\n"
                + json.dumps(
            {"requirements": requirements, "technical_proposal": technical_proposal, "catalog": catalog}, default=str,
            ensure_ascii=False)
        )
        result = self.__agent.invoke({
            "messages": [
                HumanMessage(content=prompt)
            ]
        })
        return result["structured_response"]

    async def arun(self, requirements: dict, technical_proposal: dict, catalog: list[dict]) -> FinancialEstimatorOutputSchema:
        prompt = (
                "Prepare la estimación del esfuerzo utilizando ÚNICAMENTE estos datos de entrada. La aplicación realizará "
                "el cálculo aritmético decimal final.\n\n"
                + json.dumps(
            {"requirements": requirements, "technical_proposal": technical_proposal, "catalog": catalog}, default=str,
            ensure_ascii=False)
        )
        result = await self.__agent.ainvoke({
            "messages": [
                HumanMessage(content=prompt)
            ]
        })
        return result["structured_response"]

    def unwrap(self):
        return self.__agent

