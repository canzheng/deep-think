from __future__ import annotations

from .common import append_named_list, append_named_value, legacy_section_heading


def _append_scenario(lines: list[str], label: str, scenario: dict[str, object]) -> None:
    lines.append(f"- {label}:")
    append_named_value(lines, "Name", scenario.get("name"))
    append_named_value(lines, "Summary", scenario.get("summary"))
    append_named_list(lines, "Branch points", scenario.get("branch_points"))
    append_named_list(lines, "Branch triggers", scenario.get("branch_triggers"))
    append_named_value(lines, "Reversibility", scenario.get("reversibility"))
    append_named_value(lines, "Probability logic", scenario.get("probability_logic"))
    append_named_list(lines, "Decision-mode implications", scenario.get("decision_mode_implications"))


def render_scenarios(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("scenarios")]
    base_case = payload.get("base_case")
    if isinstance(base_case, dict):
        _append_scenario(lines, "Base case", base_case)

    alternatives = payload.get("alternative_scenarios")
    if isinstance(alternatives, list) and alternatives:
        lines.append("- Alternative scenarios:")
        for scenario in alternatives:
            if not isinstance(scenario, dict):
                continue
            name = scenario.get("name", "Scenario")
            summary = scenario.get("summary", "")
            lines.append(f"  - {name}: {summary}".rstrip(": "))

    return lines
