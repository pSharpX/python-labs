from constants import AnalysisStatus, STATUS_PRIORITY


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