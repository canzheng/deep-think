from __future__ import annotations

import json
import re


LEGACY_SECTION_HEADINGS: dict[str, str] = {
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


def heading(level: int, text: str) -> str:
    return f"{'#' * level} {text}"


def legacy_section_heading(section_name: str) -> str:
    return LEGACY_SECTION_HEADINGS.get(section_name, f"### Current {section_name}:")


def json_block(payload: object) -> list[str]:
    return [
        "```json",
        json.dumps(payload, indent=2, ensure_ascii=True),
        "```",
    ]


def fenced_text_block(value: str) -> list[str]:
    backtick_runs = [len(match.group(0)) for match in re.finditer(r"`+", value)]
    fence = "`" * max(3, max(backtick_runs, default=0) + 1)
    return [f"{fence}text", value, fence]


def append_named_value(lines: list[str], label: str, value: object) -> None:
    if value in (None, "", [], {}):
        return
    lines.append(f"- {label}: {value}")


def append_named_list(lines: list[str], label: str, values: object) -> None:
    if not isinstance(values, list) or not values:
        return
    lines.append(f"- {label}:")
    for value in values:
        lines.append(f"  - {value}")
