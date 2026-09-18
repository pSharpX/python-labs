from constants import AnalysisStatus, STATUS_PRIORITY
from collections.abc import Callable
from typing import TypeVar

from models import Requirement, NonFunctionalRequirement, Actor, Process, Integration, Risk, Assumption, \
    MissingInformation, ClientQuestion


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

def merge_status(
    current: AnalysisStatus,
    update: AnalysisStatus,
) -> AnalysisStatus:
    """
    Resolve concurrent status updates deterministically.

    A more advanced state is never downgraded by another concurrent update.
    """
    if not current:
        return update

    if not update:
        return current

    return (
        update
        if STATUS_PRIORITY[update] > STATUS_PRIORITY[current]
        else current
    )

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

def merge_requirements(
    current: list[Requirement],
    updates: list[Requirement],
) -> list[Requirement]:
    return upsert_model_by_id(current, updates)

def merge_non_functional_requirements(
    current: list[Requirement],
    updates: list[Requirement],
) -> list[NonFunctionalRequirement]:
    return upsert_model_by_id(current, updates)

def merge_actors(
    current: list[Actor],
    updates: list[Actor],
) -> list[Actor]:
    return upsert_by_id(
        current,
        updates,
        key=lambda item: item.name,
    )

def merge_processes(
    current: list[Process],
    updates: list[Process],
) -> list[Process]:
    return upsert_by_id(
        current,
        updates,
        key=lambda item: item.name,
    )

def merge_integrations(
    current: list[Integration],
    updates: list[Integration],
) -> list[Integration]:
    return upsert_by_id(
        current,
        updates,
        key=lambda item: item.system,
    )

def merge_risks(
    current: list[Risk],
    updates: list[Risk],
) -> list[Risk]:
    return upsert_model_by_description(current, updates)

def merge_assumptions(
    current: list[Assumption],
    updates: list[Assumption],
) -> list[Assumption]:
    return upsert_model_by_description(current, updates)

def merge_missing_information(
    current: list[MissingInformation],
    updates: list[MissingInformation],
) -> list[MissingInformation]:
    return upsert_model_by_description(current, updates)

def merge_client_questions(
    current: list[ClientQuestion],
    updates: list[ClientQuestion],
) -> list[ClientQuestion]:
    return upsert_by_id(
        current,
        updates,
        key=lambda item: item.question,
    )