from __future__ import annotations

from collections.abc import Callable

from .common import json_block, legacy_section_heading
from .boundary import render_boundary
from .decision_logic import render_decision_logic
from .evidence_plan import render_evidence_plan
from .monitoring import render_monitoring
from .questions import render_questions
from .routing import render_routing
from .scenarios import render_scenarios
from .signals import render_signals
from .structure import render_structure
from .synthesis import render_synthesis
from .topic import render_topic
from .uncertainty_map import render_uncertainty_map


SECTION_RENDERERS: dict[str, Callable[[object], list[str]]] = {
    "topic": render_topic,
    "routing": render_routing,
    "boundary": render_boundary,
    "structure": render_structure,
    "scenarios": render_scenarios,
    "questions": render_questions,
    "evidence_plan": render_evidence_plan,
    "uncertainty_map": render_uncertainty_map,
    "decision_logic": render_decision_logic,
    "synthesis": render_synthesis,
    "signals": render_signals,
    "monitoring": render_monitoring,
}


def render_section(section_name: str, payload: object) -> list[str]:
    renderer = SECTION_RENDERERS.get(section_name)
    if renderer:
        return renderer(payload)

    return [
        legacy_section_heading(section_name),
        *json_block(payload),
    ]
