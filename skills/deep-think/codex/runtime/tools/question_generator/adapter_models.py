from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StageGuidanceEntry:
    importance: str
    guidance: str


@dataclass(frozen=True)
class TaskAdapter:
    value: str
    prioritize: list[str]
    stage_guidance: dict[str, StageGuidanceEntry]


@dataclass(frozen=True)
class DomainAdapter:
    value: str
    typical_ontology: list[str]
    typical_bottlenecks: list[str]
    typical_signals: list[str]
    stage_guidance: dict[str, StageGuidanceEntry]


@dataclass(frozen=True)
class EvidenceModeAdapter:
    value: str
    prioritize: list[str]
    strengths: list[str]
    weaknesses: list[str]
    stage_guidance: dict[str, StageGuidanceEntry]


@dataclass(frozen=True)
class UncertaintyModeAdapter:
    value: str
    research_behavior: list[str]
    risk: list[str]
    stage_guidance: dict[str, StageGuidanceEntry]


@dataclass(frozen=True)
class DecisionModeAdapter:
    value: str
    use_when: list[str]
    research_behavior: list[str]
    key_questions: list[str]
    action_logic: list[str]
    monitoring_style: list[str]
    failure_mode: list[str]
    stage_guidance: dict[str, StageGuidanceEntry]


AdapterPayload = (
    TaskAdapter
    | DomainAdapter
    | EvidenceModeAdapter
    | UncertaintyModeAdapter
    | DecisionModeAdapter
)


def load_adapter_payload(dimension: str, path: Path) -> AdapterPayload:
    payload = _load_json(path)
    guidance = _load_stage_guidance(payload["stage_guidance"])

    if dimension == "task":
        return TaskAdapter(
            value=payload["value"],
            prioritize=list(payload["prioritize"]),
            stage_guidance=guidance,
        )
    if dimension == "domain":
        return DomainAdapter(
            value=payload["value"],
            typical_ontology=list(payload["typical_ontology"]),
            typical_bottlenecks=list(payload["typical_bottlenecks"]),
            typical_signals=list(payload["typical_signals"]),
            stage_guidance=guidance,
        )
    if dimension == "evidence_mode":
        return EvidenceModeAdapter(
            value=payload["value"],
            prioritize=list(payload["prioritize"]),
            strengths=list(payload["strengths"]),
            weaknesses=list(payload["weaknesses"]),
            stage_guidance=guidance,
        )
    if dimension == "uncertainty_mode":
        return UncertaintyModeAdapter(
            value=payload["value"],
            research_behavior=list(payload["research_behavior"]),
            risk=list(payload["risk"]),
            stage_guidance=guidance,
        )
    if dimension == "decision_mode":
        return DecisionModeAdapter(
            value=payload["value"],
            use_when=list(payload["use_when"]),
            research_behavior=list(payload["research_behavior"]),
            key_questions=list(payload["key_questions"]),
            action_logic=list(payload["action_logic"]),
            monitoring_style=list(payload["monitoring_style"]),
            failure_mode=list(payload["failure_mode"]),
            stage_guidance=guidance,
        )

    raise ValueError(f"Unsupported adapter dimension: {dimension}")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open() as input_file:
        payload = json.load(input_file)
    if not isinstance(payload, dict):
        raise ValueError(f"Adapter payload must be an object: {path}")
    return payload


def _load_stage_guidance(raw: dict[str, Any]) -> dict[str, StageGuidanceEntry]:
    guidance: dict[str, StageGuidanceEntry] = {}
    for stage, value in raw.items():
        guidance[stage] = StageGuidanceEntry(
            importance=value["importance"],
            guidance=value["guidance"],
        )
    return guidance
