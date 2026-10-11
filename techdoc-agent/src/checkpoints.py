from dataclasses import dataclass
from typing import Any

from langgraph.graph.state import CompiledStateGraph


RECURSION_LIMIT = 60

@dataclass
class PendingInterrupt:
    node: str
    value: dict[str, Any]

def thread_config(thread_id: str, trace_id: str | None = None) -> dict[str, Any]:
    cfg: dict[str, Any] = {"configurable": {"thread_id": thread_id}, "recursion_limit": RECURSION_LIMIT}
    if trace_id:
        cfg["metadata"] = {"trace_id": trace_id}
        cfg["tags"] = [f"trace:{trace_id}"]
    return cfg

async def pending_interrupt(graph: CompiledStateGraph, thread_id: str) -> PendingInterrupt | None:
    snapshot = await graph.aget_state(thread_config(thread_id))
    for task in snapshot.tasks:
        for intr in task.interrupts:
            return PendingInterrupt(node=task.name, value=dict(intr.value or {}))
    return None

async def has_checkpoint(graph: CompiledStateGraph, thread_id: str) -> bool:
    snapshot = await graph.aget_state(thread_config(thread_id))
    return bool(snapshot.values)

async def is_interrupted_by_error(graph: CompiledStateGraph, thread_id: str) -> bool:
    """True when the last run stopped with pending work but no interrupt (crash/error)."""
    snapshot = await graph.aget_state(thread_config(thread_id))
    return bool(snapshot.next) and not any(t.interrupts for t in snapshot.tasks)
