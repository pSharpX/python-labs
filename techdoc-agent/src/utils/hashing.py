"""Deterministic fingerprints for artifacts and files."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def canonical_json(data: Any) -> str:
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def fingerprint(data: Any, exclude: Iterable[str] = ()) -> str:
    """SHA-256 of the canonical JSON form, ignoring top-level metadata keys in ``exclude``."""
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    if isinstance(data, dict) and exclude:
        excluded = set(exclude)
        data = {k: v for k, v in data.items() if k not in excluded}
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow() -> datetime:
    return datetime.now(UTC)
