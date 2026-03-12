from __future__ import annotations

import json
import re

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
    placeholder_values = {
        "topic": _render_topic_block(state.get("topic", "")),
        "current_state": state_block,
        "active_steering": steering_block,
        "required_output": output_block,
        "feedback": feedback_block,
    }
    rendered_template, used_placeholders = _render_template_placeholders(
        template,
        placeholder_values,
    )
    topic_only_state = list(state_sections.keys()) == ["topic"]

    blocks = [
        rendered_template,
    ]
    if (
        state_block
        and "current_state" not in used_placeholders
        and not ("topic" in used_placeholders and topic_only_state)
    ):
        blocks.append(state_block)
    if steering_block and "active_steering" not in used_placeholders:
        blocks.append(steering_block)
    if output_block and "required_output" not in used_placeholders:
        blocks.append(output_block)
    if feedback_block and "feedback" not in used_placeholders:
        blocks.append(feedback_block)

    return "\n\n".join(block for block in blocks if block)


def _render_template_placeholders(template: str, values: dict[str, str]) -> tuple[str, set[str]]:
    used_placeholders: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            return match.group(0)

        used_placeholders.add(key)
        return values.get(key, "")

    rendered = re.sub(r"\{\{\s*([a-z_]+)\s*\}\}", replace, template)
    return rendered, used_placeholders


def _render_topic_block(topic: str) -> str:
    if not topic:
        return ""

    backtick_runs = [len(match.group(0)) for match in re.finditer(r"`+", topic)]
    fence = "`" * max(3, max(backtick_runs, default=0) + 1)
    return "\n".join([f"{fence}text", topic, fence])


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
