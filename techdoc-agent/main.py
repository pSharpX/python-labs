import uuid

from src import TechDocBuilderGraph, WorkflowSnapshot
from src.shared import UserResponse, UserAction


def _ask(snap: WorkflowSnapshot) -> UserResponse:
    payload = snap.interrupt or {}
    if payload["type"] == "requirements_clarification":
        print("\nThe requirements analyst needs more information:")
        for q in payload["questions"]:
            print(f"  ? {q}")
        return UserResponse(action=UserAction.PROVIDE_INFORMATION, information=input("\nYour answer: "))

    print(payload)
    print("\n" + payload["financial_proposal"])
    while True:
        choice = input("\n[a]pprove / request [c]hanges to the estimate / change [r]equirements: ").strip().lower()
        if choice == "a":
            return UserResponse(action=UserAction.APPROVE)
        if choice == "c":
            return UserResponse(action=UserAction.REQUEST_CHANGES, feedback=input("Feedback: "))
        if choice == "r":
            return UserResponse(action=UserAction.CHANGE_REQUIREMENTS, changes=input("Requirement change: "))

def run_agent():
    workflow = TechDocBuilderGraph()
    workflow.draw_workflow()

    print("Welcome to TechDoc Builder Workflow, your helpful assistant!")
    print("Start typing ('c' for exit) >> ")

    request: str = input()
    proposal_id = str(uuid.uuid4())
    snap = workflow.start(proposal_id, request)

    while snap.waiting_for_user:
        snap = workflow.resume(proposal_id, _ask(snap))

    print(f"\nFinal status: {snap.status.value if snap.status else None}")
    if snap.values.get("errors"):
        print("Errors:", *snap.values["errors"], sep="\n  ")


if __name__ == '__main__':
    run_agent()
    # asyncio.run(start_agent())
