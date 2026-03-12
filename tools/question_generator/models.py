from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pathlib import Path


@dataclass(frozen=True)
class OptionalRead:
    stage: str
    kind: str
    when: list[str]


@dataclass(frozen=True)
class Feedback:
    supported: bool
    field: str | None = None
    schema: dict[str, Any] | None = None


@dataclass(frozen=True)
class OutputSchema:
    type: str
    required: list[str]
    properties: dict[str, Any]
    raw: dict[str, Any]


@dataclass(frozen=True)
class StageContract:
    stage: str
    depends_on: list[str]
    writes: list[str]
    output_format: str
    feedback: Feedback
    output_schema: OutputSchema
    reads_required: list[str] | None = None
    reads_optional: list[OptionalRead] | None = None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class ResolvedModule:
    dimension: str
    value: str
    path: Path
