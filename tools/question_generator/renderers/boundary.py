from __future__ import annotations

from .common import append_named_list, append_named_value, legacy_section_heading


def render_boundary(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("boundary")]
    append_named_value(lines, "Exact object of analysis", payload.get("exact_object_of_analysis"))
    append_named_value(lines, "Core system", payload.get("core_system"))
    append_named_list(lines, "Adjacent systems", payload.get("adjacent_systems"))
    append_named_list(lines, "Out-of-scope factors", payload.get("out_of_scope_factors"))
    append_named_list(lines, "Scope assumptions", payload.get("scope_assumptions"))
    return lines
