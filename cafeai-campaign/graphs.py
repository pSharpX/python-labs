from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from config import langfuse_handler
from prompts import get_creative_strategist_prompt, get_copywriter_prompt, get_visual_designer_prompt
from settings import BaseModelSettings


class AdCampaignBuilderInput(BaseModel):
    idea: str = Field(
        description="Idea o concepto principal de la campaña publicitaria que se desea desarrollar.",
    )

class AdCampaignBuilderOutput(BaseModel):
    creative_brief: str = Field(
        description="Brief creativo de la campaña, incluyendo objetivo, audiencia, mensaje clave, tono y concepto visual."
    )
    copywriter_copies: str = Field(
        description="Textos publicitarios propuestos para la campaña, adaptados al concepto, audiencia y canales definidos."
    )
    designs: str = Field(
        description="Propuestas de diseño visual para la campaña, incluyendo concepto, composición, estilo y elementos gráficos."
    )

class AdCampaignBuilderState(TypedDict):
    idea: str
    creative_brief: str
    copywriter_copies: str
    designs: str


class AdCampaignBuilderWorkflow:
    """A langgraph powered workflow that build ad campaigns."""

    def __init__(self):
        self.__settings = BaseModelSettings()
        self.__model = init_chat_model(
            model=self.__settings.model_name,
            model_provider=self.__settings.provider,
            temperature=self.__settings.temperature,
        )
        self.__builder = StateGraph(
            state_schema=AdCampaignBuilderState,
            input_schema=AdCampaignBuilderInput,
            output_schema=AdCampaignBuilderOutput,
        )
        self.graph = self.__build()

    def __creative_strategist_node(self, state: AdCampaignBuilderState):
        """Creative Strategist Node capture brand context and develop the creative concept and plan."""

        system_prompt = SystemMessage(content=get_creative_strategist_prompt())
        user_message = HumanMessage(state["idea"])
        messages = [
            system_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "creative_brief": res.content,
        }

    def __copywriter_node(self, state: AdCampaignBuilderState):
        """Copywriter Node use the creative brief to write ad messages to connect with the target."""

        system_prompt = SystemMessage(content=get_copywriter_prompt(state["idea"]))
        user_message = HumanMessage(state["creative_brief"])
        messages = [
            system_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "copywriter_copies": res.content,
        }

    def __visual_designer_node(self, state: AdCampaignBuilderState):
        """Visual Designer Node use the creative brief and the copywriter copies to transform the ad messages and ideas into consistent visual direction."""

        system_prompt = SystemMessage(content=get_visual_designer_prompt(state["idea"]))
        creative_brief_message = HumanMessage(state["creative_brief"])
        copywriter_message = HumanMessage(state["copywriter_copies"])
        messages = [
            system_prompt,
            creative_brief_message,
            copywriter_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "designs": res.content,
        }

    def __build(self):
        self.__builder.add_node("creative_strategist_node", self.__creative_strategist_node)
        self.__builder.add_node("copywriter_node", self.__copywriter_node)
        self.__builder.add_node("visual_designer_node", self.__visual_designer_node)

        self.__builder.add_edge(START, "creative_strategist_node")
        self.__builder.add_edge("creative_strategist_node", "copywriter_node")
        self.__builder.add_edge("copywriter_node", "visual_designer_node")
        self.__builder.add_edge("visual_designer_node", END)

        return self.__builder.compile(checkpointer=InMemorySaver())

    def start(self, input_obj: dict, session_id: str):
        print("Welcome to AdCampaign Builder Workflow, your helpful assistant!")
        print("Start typing ('c' for exit) >> ")
        while True:
            question = input()
            if question == "c":
                break
            elif question.strip() == "":
                continue
            state = self.graph.invoke(
                input={
                    "idea": question
                },
                config={
                    "callbacks": [langfuse_handler],
                    "metadata": {
                        "langfuse_user_id": input_obj["user_id"],
                        "langfuse_session_id": session_id,
                        "langfuse_tags": [
                            "environment:dev",
                            "framework:langgraph",
                            "application:cafeai-campaign",
                            "component:cafeai-campaign-workflow",
                        ]
                    },
                    "configurable": {
                        "thread_id": session_id
                    }
                })
            print(state)


