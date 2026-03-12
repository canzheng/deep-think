from __future__ import annotations

from .common import json_block, legacy_section_heading


def render_routing(payload: dict[str, object]) -> list[str]:
    lines = [
        legacy_section_heading("routing"),
    ]

    if question := payload.get("question"):
        lines.append(f"- Normalized question: {question}")
    if constraints := payload.get("explicit_constraints"):
        lines.append("- Explicit constraints:")
        for constraint in constraints:
            lines.append(f"  - {constraint}")
    if desired_output := payload.get("desired_output"):
        lines.append(f"- Desired output: {desired_output}")
    if risk_tolerance := payload.get("risk_tolerance"):
        lines.append(f"- Risk tolerance: {risk_tolerance}")
    if decision_context := payload.get("decision_context"):
        lines.append(f"- Decision context: {decision_context}")

    lines.extend(
        [
        f"- Task: {payload.get('task', 'N/A')}",
        f"- Domain: {payload.get('domain', 'N/A')}",
        f"- Output mode: {payload.get('output_mode', 'N/A')}",
        f"- Evidence mode: {payload.get('evidence_mode', 'N/A')}",
        f"- Uncertainty mode: {payload.get('uncertainty_mode', 'N/A')}",
        f"- Decision mode: {payload.get('decision_mode', 'N/A')}",
        ]
    )

    if time_horizon := payload.get("time_horizon"):
        lines.append(f"- Time horizon: {time_horizon}")

    if unit_of_analysis := payload.get("unit_of_analysis"):
        lines.append(f"- Unit of analysis: {unit_of_analysis}")

    assumptions = payload.get("assumptions") or payload.get("key_assumptions")
    if isinstance(assumptions, list) and assumptions:
        lines.append("- Assumptions:")
        for assumption in assumptions:
            lines.append(f"  - {assumption}")

    return [
        *lines,
        *json_block(payload),
    ]
