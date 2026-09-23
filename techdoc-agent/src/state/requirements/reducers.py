from src.shared import (
    upsert_model_by_id,
    upsert_by_key,
    upsert_model_by_description
)
from src.state.models import Requirement, NonFunctionalRequirement, Actor, Process, Integration, Risk, Assumption, \
    MissingInformation, ClientQuestion


def merge_requirements(
    current: list[Requirement],
    updates: list[Requirement],
) -> list[Requirement]:
    return upsert_model_by_id(current, updates, model_type=Requirement)

def merge_non_functional_requirements(
    current: list[NonFunctionalRequirement],
    updates: list[NonFunctionalRequirement],
) -> list[NonFunctionalRequirement]:
    return upsert_model_by_id(current, updates, model_type=NonFunctionalRequirement)

def merge_actors(
    current: list[Actor],
    updates: list[Actor],
) -> list[Actor]:
    return upsert_by_key(
        current,
        updates,
        model_type=Actor,
        key=lambda item: item.name,
    )

def merge_processes(
    current: list[Process],
    updates: list[Process],
) -> list[Process]:
    return upsert_by_key(
        current,
        updates,
        model_type=Process,
        key=lambda item: item.name,
    )

def merge_integrations(
    current: list[Integration],
    updates: list[Integration],
) -> list[Integration]:
    return upsert_by_key(
        current,
        updates,
        model_type=Integration,
        key=lambda item: item.system,
    )

def merge_risks(
    current: list[Risk],
    updates: list[Risk],
) -> list[Risk]:
    return upsert_model_by_description(current, updates, model_type=Risk)

def merge_assumptions(
    current: list[Assumption],
    updates: list[Assumption],
) -> list[Assumption]:
    return upsert_model_by_description(current, updates, model_type=Assumption)

def merge_missing_information(
    current: list[MissingInformation],
    updates: list[MissingInformation],
) -> list[MissingInformation]:
    return upsert_model_by_description(current, updates, model_type=MissingInformation)

def merge_client_questions(
    current: list[ClientQuestion],
    updates: list[ClientQuestion],
) -> list[ClientQuestion]:
    return upsert_by_key(
        current,
        updates,
        model_type=ClientQuestion,
        key=lambda item: item.question,
    )