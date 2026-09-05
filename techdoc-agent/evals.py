import uuid

import pytest
from deepeval import assert_test
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import TaskCompletionMetric, ToolCorrectnessMetric
from deepeval.test_case import ToolCall, ToolCallParams, LLMTestCase

from agents import TechDocAgent
from settings import BaseModelSettings

golden_input = """
# Requerimientos — Sistema de Envío de Correos Masivos ## Objetivo Construir una plataforma web para gestionar y enviar campañas de correos masivos, desplegada sobre Microsoft Azure. ## Requerimientos funcionales * Autenticación y gestión de usuarios con acceso restringido. * Gestión de listas de destinatarios. * Importación de destinatarios mediante CSV/Excel. * Creación y edición de campañas. * Definición de asunto, remitente, contenido HTML y destinatarios. * Envío inmediato o programado. * Procesamiento asíncrono de los envíos. * Reintentos ante errores y control de envíos duplicados. * Consulta del estado e historial de campañas. * Reporte básico de enviados, fallidos y pendientes. ## Requerimientos técnicos * Despliegue en Microsoft Azure. * Uso de un servicio especializado para envío de correos. * Procesamiento mediante colas o mecanismo equivalente. * Base de datos para usuarios, destinatarios, campañas y resultados. * Seguridad, gestión de secretos y acceso mediante HTTPS. * Logging y monitoreo. * Arquitectura preparada para escalar el volumen de envíos. ## Consideraciones El número de usuarios será limitado. El volumen máximo de destinatarios, frecuencia de campañas y proveedor de correo deberán definirse durante el diseño de la solución.
"""
dataset = EvaluationDataset(goldens=[Golden(input=golden_input)])
model_settings = BaseModelSettings()


TOOL_CORRECTNESS_TEST_CASES = [
    {
        "user_input": golden_input,
        "expected_tools": [
            ToolCall(
                name="save_markdown",
                input_parameters={},
            )
        ],
    },
    {
        "user_input": "Explain what Clean Architecture is.",
        "expected_tools": [],
    },
]


def extract_tool_calls(result) -> list[ToolCall]:
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


@pytest.fixture
def agent():
    return TechDocAgent().unwrap()

@pytest.mark.parametrize("golden", dataset.goldens)
def test_task_completion(agent, golden: Golden):
    task_completion = TaskCompletionMetric(
        threshold=0.8,
        model=model_settings.model_name,
    )
    agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={
            "callbacks": [CallbackHandler()],
            "configurable": { "thread_id": str(uuid.uuid4()) }
        },
    )
    assert_test(golden=golden, metrics=[task_completion])

@pytest.mark.parametrize("test_case", TOOL_CORRECTNESS_TEST_CASES)
def test_tool_correctness(agent, test_case):
    # Arrange
    metric = ToolCorrectnessMetric(
        threshold=0.8,
        include_reason=True,
        model=model_settings.model_name,
        should_consider_ordering=True,
    )

    # Act
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": test_case["user_input"],
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": f"deepeval-{uuid.uuid4()}",
            }
        },
    )

    actual_tools = extract_tool_calls(result)
    test_case = LLMTestCase(
        input=test_case["user_input"],
        actual_output=result["messages"][-1].content,
        tools_called=actual_tools,
        expected_tools=test_case["expected_tools"],
    )

    # Assert
    metric.measure(test_case)
    assert_test(
        test_case,
        [metric],
    )
