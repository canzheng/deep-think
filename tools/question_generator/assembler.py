from __future__ import annotations

import json

from tools.question_generator.adapter_rendering import render_adapter_sections
from tools.question_generator.adapter_resolution import resolve_stage_modules
from tools.question_generator.contracts import load_contract
from tools.question_generator.pathing import stage_template_path
from tools.question_generator.state_rendering import render_state_sections
from tools.question_generator.state_resolution import resolve_state_sections


def assemble_stage_prompt(
    stage: str,
    state: dict,
    optional_reads: list[str] | None = None,
) -> str:
    contract = load_contract(stage)
    template = stage_template_path(stage).read_text().strip()
    state_sections = resolve_state_sections(contract, state, optional_reads=optional_reads)
    state_block = render_state_sections(stage, state_sections)
    modules = resolve_stage_modules(contract, state.get("routing", {}))
    steering_block = render_adapter_sections(stage, modules) if modules else ""
    output_block = _render_required_output(contract.output_schema.raw)
    feedback_block = _render_feedback(contract.feedback.schema) if contract.feedback.supported else ""

    blocks = [
        template,
        state_block,
    ]
    if steering_block:
        blocks.append(steering_block)
    blocks.append(output_block)
    if feedback_block:
        blocks.append(feedback_block)

    return "\n\n".join(block for block in blocks if block)


def _render_required_output(output_schema: dict) -> str:
    return "\n".join(
        [
            "## Required Output",
            "```json",
            json.dumps(output_schema, indent=2, ensure_ascii=True),
            "```",
        ]
    )


def _render_feedback(feedback_schema: dict) -> str:
    return "\n".join(
        [
            "## Feedback",
            "```json",
            json.dumps(feedback_schema, indent=2, ensure_ascii=True),
            "```",
        ]
    )
