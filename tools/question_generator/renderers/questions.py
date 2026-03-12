from __future__ import annotations

from .common import legacy_section_heading


QUESTION_BUCKETS = [
    ("top_killer_questions", "Top killer questions"),
    ("clarifying", "Clarifying questions"),
    ("structural", "Structural questions"),
    ("stakeholder", "Stakeholder questions"),
    ("evidence", "Evidence questions"),
    ("task_specific", "Task-specific questions"),
    ("domain_specific", "Domain-specific questions"),
    ("output_mode_specific", "Output-mode-specific questions"),
    ("evidence_mode_specific", "Evidence-mode-specific questions"),
    ("uncertainty_mode_specific", "Uncertainty-mode-specific questions"),
    ("decision_mode_specific", "Decision-mode-specific questions"),
]


def render_questions(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("questions")]
    for key, label in QUESTION_BUCKETS:
        questions = payload.get(key)
        if not isinstance(questions, list) or not questions:
            continue

        lines.append(f"- {label}:")
        for item in questions:
            if not isinstance(item, dict):
                continue
            question = item.get("question")
            why_it_matters = item.get("why_it_matters")
            if question:
                lines.append(f"  - {question}")
            if why_it_matters:
                lines.append(f"    Why it matters: {why_it_matters}")
    return lines
