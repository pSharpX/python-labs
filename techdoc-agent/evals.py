import uuid

import pytest
from deepeval import assert_test
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.integrations.langchain import CallbackHandler
from deepeval.metrics import TaskCompletionMetric
from deepeval.test_case import ToolCall

from agents import TechDocAgent
from evaluators import TechDocAgentEvaluator

golden_input = """
# Requerimientos — Sistema de Envío de Correos Masivos ## Objetivo Construir una plataforma web para gestionar y enviar campañas de correos masivos, desplegada sobre Microsoft Azure. ## Requerimientos funcionales * Autenticación y gestión de usuarios con acceso restringido. * Gestión de listas de destinatarios. * Importación de destinatarios mediante CSV/Excel. * Creación y edición de campañas. * Definición de asunto, remitente, contenido HTML y destinatarios. * Envío inmediato o programado. * Procesamiento asíncrono de los envíos. * Reintentos ante errores y control de envíos duplicados. * Consulta del estado e historial de campañas. * Reporte básico de enviados, fallidos y pendientes. ## Requerimientos técnicos * Despliegue en Microsoft Azure. * Uso de un servicio especializado para envío de correos. * Procesamiento mediante colas o mecanismo equivalente. * Base de datos para usuarios, destinatarios, campañas y resultados. * Seguridad, gestión de secretos y acceso mediante HTTPS. * Logging y monitoreo. * Arquitectura preparada para escalar el volumen de envíos. ## Consideraciones El número de usuarios será limitado. El volumen máximo de destinatarios, frecuencia de campañas y proveedor de correo deberán definirse durante el diseño de la solución.
"""
dataset = EvaluationDataset(goldens=[Golden(input=golden_input)])

task_completion = TaskCompletionMetric(
    threshold=0.8,
    model="gpt-4o"
)


agent = TechDocAgent().unwrap()
evaluator = TechDocAgentEvaluator(agent)

TEST_CASES = [
    {
        "input": golden_input,
        "expected_tools": [
            ToolCall(
                name="save_markdown",
                input_parameters={
                    "filename": "proposal.md",
                    "content": "# Technical Proposal",
                },
            )
        ],
    },
    {
        "input": "Explain what Clean Architecture is.",
        "expected_tools": [],
    },
]

@pytest.mark.parametrize("golden", dataset.goldens)
def test_techdoc_agent(golden: Golden):
    agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={
            "callbacks": [CallbackHandler()],
            "configurable": { "thread_id": str(uuid.uuid4()) }
        },
    )
    assert_test(golden=golden, metrics=[task_completion])



for i, test in enumerate(TEST_CASES):
    result = evaluator.run(
        user_input=test["input"],
        expected_tools=test["expected_tools"],
    )

    print(f"\nTest {i + 1}")
    print(f"Score: {result['score']}")
    print(f"Reason: {result['reason']}")
    print(f"Tools: {result['tools_called']}")