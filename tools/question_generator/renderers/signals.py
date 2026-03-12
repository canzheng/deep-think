from __future__ import annotations

from .common import append_named_list, append_named_value, legacy_section_heading


def render_signals(payload: object) -> list[str]:
    lines = [legacy_section_heading("signals")]
    if not isinstance(payload, list):
        return lines

    for signal in payload:
        if not isinstance(signal, dict):
            continue
        lines.append(f"- Signal: {signal.get('signal', 'Unknown signal')}")
        append_named_value(lines, "Linked question", signal.get("linked_question"))
        append_named_value(lines, "Preferred evidence source", signal.get("preferred_evidence_source"))
        append_named_value(lines, "Backup evidence source", signal.get("backup_evidence_source"))
        append_named_value(lines, "Cadence", signal.get("cadence"))
        append_named_list(lines, "Thresholds", signal.get("thresholds"))
        append_named_list(lines, "Update rules", signal.get("update_rules"))
        append_named_list(lines, "Belief-update implications", signal.get("belief_update_implications"))
        append_named_value(
            lines,
            "Confidence under current uncertainty mode",
            signal.get("confidence_under_current_uncertainty_mode"),
        )
        append_named_value(lines, "Changes action vs belief", signal.get("changes_action_vs_belief"))
    return lines
