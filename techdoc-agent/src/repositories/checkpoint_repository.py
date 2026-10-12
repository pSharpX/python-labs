from __future__ import annotations

from contextlib import AsyncExitStack

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from config import serde
from settings import DatabaseSettings


async def open_checkpointer(settings: DatabaseSettings, stack: AsyncExitStack) -> BaseCheckpointSaver:
    backend = settings.checkpoint_backend
    if backend == "memory":
        return InMemorySaver(serde=serde)
    if backend == "postgres":
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        except ImportError as exc:
            raise RuntimeError(
                "Postgres checkpoints need: pip install langgraph-checkpoint-postgres 'psycopg[binary,pool]'"
            ) from exc
        saver = await stack.enter_async_context(AsyncPostgresSaver.from_conn_string(settings.checkpoint_url))
        await saver.setup()
        return saver
    raise ValueError(f"Unknown checkpoint backend: {backend}")
