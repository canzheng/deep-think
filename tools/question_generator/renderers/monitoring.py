from __future__ import annotations

from .common import append_named_list, append_named_value, legacy_section_heading


def render_monitoring(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("monitoring")]

    watch_items = payload.get("what_to_watch")
    if isinstance(watch_items, list) and watch_items:
        lines.append("- What to watch:")
        for item in watch_items:
            if not isinstance(item, dict):
                continue
            lines.append(f"  - {item.get('item', 'Unknown item')}")
            if why_it_matters := item.get("why_it_matters"):
                lines.append(f"    Why it matters: {why_it_matters}")
            if cadence := item.get("update_cadence"):
                lines.append(f"    Update cadence: {cadence}")
            for label, key in (
                ("Evidence source preference", "evidence_source_preference"),
                ("Escalation triggers", "escalation_triggers"),
                ("Action triggers", "action_triggers"),
                ("Noise to ignore", "noise_to_ignore"),
            ):
                values = item.get(key)
                if isinstance(values, list) and values:
                    lines.append(f"    {label}:")
                    for value in values:
                        lines.append(f"      - {value}")

    append_named_value(
        lines,
        "Signal most reducing dominant uncertainty",
        payload.get("signal_most_reducing_dominant_uncertainty"),
    )
    append_named_value(
        lines,
        "Signal most likely to change action",
        payload.get("signal_most_likely_to_change_action"),
    )
    append_named_list(lines, "What to monitor next", payload.get("what_to_monitor_next"))
    return lines
