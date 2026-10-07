import asyncio
import uuid

from src import TechDocBuilderGraph, WorkflowSnapshot
from src.shared import UserResponse, UserAction
from src.tools.mcp import MCPToolsAdapter, MCPSettings


def _ask(snap: WorkflowSnapshot) -> UserResponse:
    payload = snap.interrupt or {}
    print(payload)

    interrupt_type = payload["type"]
    if interrupt_type == "requirements_clarification":
        print("\nSe necesita mayor información para continuar con el analisis:")
        questions = payload["questions"]
        for idx, q in enumerate(questions):
            print(f"{idx+1}. {q["question"]}")
        answers = input("\nRespuesta: ")
        return UserResponse(action=UserAction.PROVIDE_INFORMATION, information=answers)

    if interrupt_type == "financial_approval":
        print("\n" + payload["financial_proposal"])
        while True:
            choice = input("\n[a]pprove / request [c]hanges to the estimate / change [r]equirements: ").strip().lower()
            if choice == "a":
                return UserResponse(action=UserAction.APPROVE)
            if choice == "c":
                return UserResponse(action=UserAction.REQUEST_CHANGES, feedback=input("Feedback: "))
            if choice == "r":
                return UserResponse(action=UserAction.CHANGE_REQUIREMENTS, changes=input("Requirement change: "))
    raise ValueError("Invalid interrupt type")

async def run_agent():
    mcp_settings = MCPSettings()
    mcp_adapter = await MCPToolsAdapter.acreate(mcp_settings)
    workflow = TechDocBuilderGraph(mcp_adapter)
    workflow.draw_workflow()

    print("Welcome to TechDoc Builder Workflow, your helpful assistant!")
    print("Start typing ('c' for exit) >> ")

    request: str = input()
    proposal_id = str(uuid.uuid4())
    snap = await workflow.start(proposal_id, request)

    while snap.waiting_for_user:
        response: UserResponse = _ask(snap)
        snap = await workflow.resume(proposal_id, response)

    print(f"\nFinal status: {snap.status if snap.status else None}")
    if snap.values.get("errors"):
        print("Errors:", *snap.values["errors"], sep="\n  ")


if __name__ == '__main__':
    # run_agent()
    asyncio.run(run_agent())
