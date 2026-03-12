from __future__ import annotations

from .common import append_named_list, append_named_value, legacy_section_heading


def render_synthesis(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("synthesis")]
    append_named_value(lines, "Recommendation or action frame", payload.get("recommendation_or_action_frame"))
    append_named_value(lines, "Why now or why not now", payload.get("why_now_or_why_not_now"))
    append_named_list(lines, "What must be true", payload.get("what_must_be_true"))
    append_named_list(lines, "Key risks and failure modes", payload.get("key_risks_and_failure_modes"))
    return lines
