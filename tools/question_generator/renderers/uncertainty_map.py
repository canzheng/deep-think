from __future__ import annotations

from .common import append_named_list, legacy_section_heading


def render_uncertainty_map(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("uncertainty_map")]
    append_named_list(lines, "Reducible unknowns", payload.get("reducible_unknowns"))
    append_named_list(lines, "Partially reducible unknowns", payload.get("partially_reducible_unknowns"))
    append_named_list(lines, "Irreducible uncertainties", payload.get("irreducible_uncertainties"))
    append_named_list(lines, "Task-material uncertainties", payload.get("task_material_uncertainties"))
    return lines
