from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")

def replace_string(current: str | None, update: str | None) -> str | None:
    """Replace a scalar value with the latest non-empty update."""
    if update is None or not update.strip():
        return current

    return update

def merge_strings(
    current: list[str],
    updates: list[str],
) -> list[str]:
    """Merge string lists while preserving insertion order."""
    result = list(current or [])

    for item in updates or []:
        if item not in result:
            result.append(item)

    return result

def upsert_by_id(
    current: list[T],
    updates: list[T],
    key: Callable[[T], str],
) -> list[T]:
    """
    Merge entities by stable identifier.

    An incoming entity replaces the existing entity with the same key.
    New entities are appended.
    """
    result = list(current or [])

    index = {
        key(item): position
        for position, item in enumerate(result)
    }

    for update in updates or []:
        update_key = key(update)

        if update_key in index:
            result[index[update_key]] = update
        else:
            index[update_key] = len(result)
            result.append(update)

    return result

def upsert_model_by_id(
    current: list[T],
    updates: list[T],
) -> list[T]:
    return upsert_by_id(
        current,
        updates,
        key=lambda item: item.id,
    )

def upsert_model_by_description(
    current: list[T],
    updates: list[T],
) -> list[T]:
    return upsert_by_id(
        current,
        updates,
        key=lambda item: item.description,
    )
