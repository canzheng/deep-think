from __future__ import annotations

from .common import fenced_text_block, legacy_section_heading


def render_topic(payload: str) -> list[str]:
    if not payload:
        body: list[str] = []
    else:
        body = fenced_text_block(payload)

    return [
        legacy_section_heading("topic"),
        *body,
    ]
