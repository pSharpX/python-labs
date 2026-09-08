from typing import TypedDict, Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

from config import langfuse_handler
from prompts import get_creative_strategist_prompt, get_copywriter_prompt, get_visual_designer_prompt, get_router_prompt
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


class SmartAdCampaignBuilderInput(AdCampaignBuilderInput):
    user_request: str = Field(
        description="Solicitud o instrucciones detalladas del usuario para personalizar la campaña.",
    )

class SmartAdCampaignBuilderState(AdCampaignBuilderState):
    user_request: str
    route: str
    reason: str
    operation: Literal["CREATE", "UPDATE"]

AdCampaignRoute = Literal["NEW_CAMPAIGN", "CREATIVE", "COPYWRITER", "DESIGNER", "FULL_CAMPAIGN", "OFF_TOPIC"]

class AdCampaignRouterOutput(BaseModel):
    route: AdCampaignRoute = Field(
        description="Ruta, destino o agente seleccionado para procesar la campaña publicitaria.",
    )
    reason: str = Field(
        description="Justificación o razón por la cual se eligió esta ruta específica.",
    )
    operation: str = Field(
        description="Indica si se crea o se actualiza una campaña publicitaria.",
    )

class SmartAdCampaignBuilderWorkflow:
    """A langgraph powered workflow that routes and delegate ad campaigns creation to nodes."""

    def __init__(self):
        self.__settings = BaseModelSettings()
        self.__router_model = init_chat_model(
            model=self.__settings.model_name,
            model_provider=self.__settings.provider,
            temperature=self.__settings.temperature,
        ).with_structured_output(AdCampaignRouterOutput)
        self.__model = init_chat_model(
            model=self.__settings.model_name,
            model_provider=self.__settings.provider,
            temperature=self.__settings.temperature,
        )
        self.__builder = StateGraph(
            state_schema=SmartAdCampaignBuilderState,
            input_schema=SmartAdCampaignBuilderInput,
            output_schema=AdCampaignBuilderOutput,
        )
        self.graph = self.__build()

    def __router_node(self, state: SmartAdCampaignBuilderState):
        """Router Node which capture user request and delegate to the appropriate node."""

        system_prompt = SystemMessage(content=get_router_prompt())
        user_message = HumanMessage(state["user_request"])
        messages = [
            system_prompt,
            user_message,
        ]
        res = self.__router_model.invoke(messages)
        return {
            "route": res.route,
            "operation": res.operation,
            "reason": res.reason,
        }

    @staticmethod
    def __pick_retriever(
            state: SmartAdCampaignBuilderState,
    ) -> Literal["creative_strategist_node", "copywriter_node", "visual_designer_node", END]:
        if state["route"] in ["NEW_CAMPAIGN", "CREATIVE", "FULL_CAMPAIGN"]:
            return "creative_strategist_node"
        elif state["route"] == "COPYWRITER":
            return "copywriter_node"
        elif state["route"] == "DESIGNER":
            return "visual_designer_node"
        else:
            return END

    def __creative_strategist_node(self, state: SmartAdCampaignBuilderState):
        """Creative Strategist Node capture brand context and develop the creative concept and plan."""

        system_prompt = SystemMessage(content=get_creative_strategist_prompt())
        message_content = f"""
        MODE = {state["operation"]}
        BRAND CONTEXT = {state["idea"]}
        """
        user_message = HumanMessage(content=message_content)
        messages = [
            system_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "creative_brief": res.content,
        }

    def __copywriter_node(self, state: SmartAdCampaignBuilderState):
        """Copywriter Node use the creative brief to write ad messages to connect with the target."""

        system_prompt = SystemMessage(content=get_copywriter_prompt(state["idea"]))
        message_content = f"""
        MODE = {state["operation"]}
        CREATIVE BRIEF = {state["creative_brief"]}
        """
        user_message = HumanMessage(message_content)
        messages = [
            system_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "copywriter_copies": res.content,
        }

    def __visual_designer_node(self, state: SmartAdCampaignBuilderState):
        """Visual Designer Node use the creative brief and the copywriter copies to transform the ad messages and ideas into consistent visual direction."""

        system_prompt = SystemMessage(content=get_visual_designer_prompt(state["idea"]))
        message_content = f"""
        MODE = {state["operation"]}
        CREATIVE BRIEF = {state["creative_brief"]}
        COPYWRITER COPIES = {state["copywriter_copies"]}
        """
        user_message = HumanMessage(message_content)
        messages = [
            system_prompt,
            user_message,
        ]
        res = self.__model.invoke(messages)
        return {
            "designs": res.content,
        }

    def __build(self):
        self.__builder.add_node("router_node", self.__router_node)
        self.__builder.add_node("creative_strategist_node", self.__creative_strategist_node)
        self.__builder.add_node("copywriter_node", self.__copywriter_node)
        self.__builder.add_node("visual_designer_node", self.__visual_designer_node)

        self.__builder.add_edge(START, "router_node")
        self.__builder.add_conditional_edges("router_node", self.__pick_retriever)
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
                    "user_request": question,
                    "idea": "Café donde la tecnología y el sabor convergen, tu espacio para conectar, crear e innovar, una taza a la vez. Diseñado como un café inteligente para mentes creativas, con conexión rápida, café excepcional y un ambiente pensado para que tus mejores ideas florezcan. Aquí, café más IA equivale a tu nuevo espacio de trabajo donde la creatividad se sirve con crema. Un lugar destinado a innovadores, desarrolladores y soñadores que entienden que la mejor idea surge en una buena conversación, con datos, diálogos y el café más inteligente de la ciudad en la misma mesa."
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
                            "component:cafeai-adcampaign-workflow",
                        ]
                    },
                    "configurable": {
                        "thread_id": session_id
                    }
                })
            print(state)


