from __future__ import annotations

from .common import append_named_list, append_named_value, legacy_section_heading


def render_decision_logic(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("decision_logic")]
    append_named_list(lines, "Must know before action", payload.get("must_know_before_action"))
    append_named_list(lines, "Can learn after action", payload.get("can_learn_after_action"))
    append_named_value(lines, "Evidence threshold", payload.get("appropriate_evidence_threshold"))
    append_named_value(lines, "Reversibility logic", payload.get("reversibility_logic"))
    append_named_value(lines, "Sizing logic", payload.get("sizing_logic"))
    append_named_value(lines, "Staging logic", payload.get("staging_logic"))
    append_named_list(lines, "Hedge / exit / kill criteria", payload.get("hedge_exit_kill_criteria"))
    append_named_list(lines, "Triggers", payload.get("triggers"))
    return lines
