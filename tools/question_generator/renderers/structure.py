from __future__ import annotations

from .common import append_named_list, legacy_section_heading


def render_structure(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("structure")]
    append_named_list(lines, "Stakeholders", payload.get("stakeholders"))
    append_named_list(lines, "Decisive stakeholders", payload.get("decisive_stakeholders"))
    append_named_list(lines, "Incentives", payload.get("incentives"))
    append_named_list(lines, "Constraints", payload.get("constraints"))
    append_named_list(lines, "Causal mechanism", payload.get("causal_mechanism"))
    append_named_list(lines, "Killer variables", payload.get("killer_variables"))
    append_named_list(lines, "Bottlenecks", payload.get("bottlenecks"))
    append_named_list(lines, "Threshold variables", payload.get("threshold_variables"))
    append_named_list(lines, "Scarce resources", payload.get("scarce_resources"))
    return lines
