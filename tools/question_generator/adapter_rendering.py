from __future__ import annotations

import re

from tools.question_generator.models import ResolvedModule
from tools.question_generator.pathing import normalize_stage_name


STAGE_LABELS = {
    "routing": "Routing",
    "boundary": "Boundary",
    "structure": "Structure",
    "scenarios": "Scenarios",
    "question_generation": "Question Generation",
    "evidence_planning": "Evidence Planning",
    "decision_logic": "Decision Logic",
    "signal_translation": "Signal Translation",
    "monitoring": "Monitoring",
    "render": "Render",
}

WRAPPER_TEMPLATES = {
    "task": "### Because this is a `{value}` task, apply this steering:",
    "domain": "### Because this problem sits in `{value}`, apply this steering:",
    "evidence_mode": "### Because the preferred evidence mode is `{value}`, apply this steering:",
    "uncertainty_mode": "### Because the dominant uncertainty is `{value}`, apply this steering:",
    "decision_mode": "### Because the action problem is `{value}`, apply this steering:",
    "output_mode": "### Because the deliverable is `{value}`, apply this steering:",
}


def render_adapter_sections(stage: str, resolved_modules: dict[str, ResolvedModule]) -> str:
    rendered = ["## Stage Guidance"]
    for dimension in resolved_modules:
        module = resolved_modules[dimension]
        rendered.extend(
            [
                WRAPPER_TEMPLATES[dimension].format(value=module.value),
                _extract_stage_steering(module, stage),
            ]
        )

    return "\n".join(rendered)


def _extract_stage_steering(module: ResolvedModule, stage: str) -> str:
    content = module.path.read_text()
    if module.dimension == "output_mode":
        if normalize_stage_name(stage) == "render":
            return content.strip()
        return _render_non_render_output_mode_guidance(module.value)

    stage_relevance = content.split("## Stage Relevance", maxsplit=1)[-1]
    desired_label = STAGE_LABELS[normalize_stage_name(stage)]
    current_label = None
    relevance = None
    collected_lines: list[str] = []

    for line in stage_relevance.splitlines():
        heading_match = re.match(
            r"^([A-Za-z /-]+) — (Primary|Modulating|Light|None)\s*$",
            line.strip(),
        )
        if heading_match:
            current_label = heading_match.group(1)
            if current_label == desired_label:
                relevance = heading_match.group(2)
                collected_lines = []
            elif relevance is not None:
                break
            continue

        if relevance is not None and line.strip():
            collected_lines.append(line.rstrip())

    body_lines = [f"Relevance: {relevance}"] if relevance is not None else []
    body_lines.extend(collected_lines)
    return "\n".join(body_lines).strip()


def _render_non_render_output_mode_guidance(output_mode: str) -> str:
    return "\n".join(
        [
            "Relevance: Modulating",
            f"- Keep this stage consistent with the eventual `{output_mode}` deliverable.",
            "- Let the deliverable shape influence emphasis and prioritization, not final section formatting.",
            "- Do not drift into writing the final artifact in this stage.",
        ]
    )
