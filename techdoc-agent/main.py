import uuid

from agents import TechDocAgent
from graphs import OrchestratorAgent


def start_agent():
    agent = OrchestratorAgent()
    agent.start(
        input_obj={
            "user_id": str(uuid.uuid4()),
        },
        session_id=str(uuid.uuid4())
    )

if __name__ == '__main__':
    start_agent()