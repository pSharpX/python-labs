from collections.abc import Callable
from typing import TypeVar, Sequence, Any

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def replace_string(current: str | None, update: str | None) -> str | None:
    """Replace a scalar value with the latest non-empty update."""
    if update is None or not update.strip():
        return current

    return update

def merge_strings(
    current: list[str] | None,
    updates: list[str] | None,
) -> list[str]:
    """Merge string lists while preserving insertion order."""
    result = list(current or [])

    for item in updates or []:
        if item not in result:
            result.append(item)

    return result

def normalize_models(
    values: Sequence[T | dict[str, Any]] | None,
    model_type: type[T],
) -> list[T]:
    """
    Normalize checkpoint-restored dictionaries and Pydantic models
    into a consistent list of Pydantic models.
    """
    result: list[T] = []

    for value in values or []:
        if isinstance(value, model_type):
            result.append(value)
        elif isinstance(value, dict):
            result.append(model_type.model_validate(value))
        else:
            raise TypeError(
                f"Expected {model_type.__name__} or dict, "
                f"got {type(value).__name__}"
            )

    return result

def upsert_by_key(
    current: Sequence[T | dict[str, Any]] | None,
    updates: Sequence[T | dict[str, Any]] | None,
    *,
    model_type: type[T],
    key: Callable[[T], str],
) -> list[T]:
    """
    Merge entities using a stable business key.

    Dictionaries are normalized to Pydantic models before
    accessing their attributes.

    Existing entities are replaced.
    New entities are appended.
    """

    current_models = normalize_models(
        current,
        model_type,
    )

    update_models = normalize_models(
        updates,
        model_type,
    )

    result = list(current_models)

    index = {
        key(item): position
        for position, item in enumerate(result)
    }

    for update in update_models:
        update_key = key(update)

        if update_key in index:
            result[index[update_key]] = update
        else:
            index[update_key] = len(result)
            result.append(update)

    return result

def upsert_model_by_id(
    current: Sequence[T | dict[str, Any]] | None,
    updates: Sequence[T | dict[str, Any]] | None,
    *,
    model_type: type[T],
) -> list[T]:
    return upsert_by_key(
        current,
        updates,
        model_type=model_type,
        key=lambda item: item.id,
    )

def upsert_model_by_description(
    current: Sequence[T | dict[str, Any]] | None,
    updates: Sequence[T | dict[str, Any]] | None,
    *,
    model_type: type[T],
) -> list[T]:
    return upsert_by_key(
        current,
        updates,
        model_type=model_type,
        key=lambda item: item.description,
    )
