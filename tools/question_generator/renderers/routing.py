from __future__ import annotations

from .common import legacy_section_heading


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

    for label, field in [
        ("Primary task", "task"),
        ("Primary domain", "domain"),
        ("Primary output mode", "output_mode"),
        ("Primary evidence mode", "evidence_mode"),
        ("Primary uncertainty mode", "uncertainty_mode"),
        ("Primary decision mode", "decision_mode"),
    ]:
        if value := payload.get(field):
            lines.append(f"- {label}: {value}")

    for label, field in [
        ("Secondary task", "secondary_task"),
        ("Secondary domain", "secondary_domain"),
        ("Secondary output mode", "secondary_output_mode"),
        ("Secondary evidence mode", "secondary_evidence_mode"),
        ("Secondary uncertainty mode", "secondary_uncertainty_mode"),
        ("Secondary decision mode", "secondary_decision_mode"),
    ]:
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            lines.append(f"- {label}: {value}")

    if time_horizon := payload.get("time_horizon"):
        lines.append(f"- Time horizon: {time_horizon}")

    if unit_of_analysis := payload.get("unit_of_analysis"):
        lines.append(f"- Unit of analysis: {unit_of_analysis}")

    assumptions = payload.get("assumptions") or payload.get("key_assumptions")
    if isinstance(assumptions, list) and assumptions:
        lines.append("- Assumptions:")
        for assumption in assumptions:
            lines.append(f"  - {assumption}")

    return lines
