from __future__ import annotations

import json


SECTION_HEADINGS = {
    "topic": "### The current topic is:",
    "routing": "### The current routing for this run is:",
    "boundary": "### The current boundary for this problem is:",
    "structure": "### The current structural view of the system is:",
    "scenarios": "### The current scenario map suggests these paths:",
    "questions": "### The current question set is:",
    "evidence_plan": "### The current evidence plan is:",
    "uncertainty_map": "### The current uncertainty map is:",
    "decision_logic": "### The current decision logic is:",
    "synthesis": "### The current synthesis is:",
    "signals": "### The current signal design is:",
    "monitoring": "### The current monitoring layer is:",
}


def render_state_sections(stage: str, sections: dict[str, object]) -> str:
    rendered_sections = ["## Current State"]
    for section_name, payload in sections.items():
        heading = SECTION_HEADINGS.get(section_name, f"### Current {section_name}:")
        rendered_sections.extend(
            [
                heading,
                "```json",
                json.dumps(payload, indent=2, ensure_ascii=True),
                "```",
            ]
        )

    return "\n".join(rendered_sections)
