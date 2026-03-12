from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

from tools.question_generator.adapter_rendering import render_adapter_sections
from tools.question_generator.adapter_resolution import resolve_stage_modules
from tools.question_generator.contracts import load_contract
from tools.question_generator.pathing import contract_path, stage_template_path
from tools.question_generator.state_rendering import render_state_sections
from tools.question_generator.state_resolution import resolve_state_sections


def assemble_stage_prompt(
    stage: str,
    state: dict,
    optional_reads: list[str] | None = None,
) -> str:
    contract_file = contract_path(stage)
    contract = load_contract(stage)
    template = stage_template_path(stage).read_text().strip()
    state_sections = resolve_state_sections(contract, state, optional_reads=optional_reads)
    state_block = render_state_sections(stage, state_sections)
    modules = resolve_stage_modules(contract, state.get("routing", {}))
    steering_block = render_adapter_sections(stage, modules) if modules else ""
    output_block = _render_required_output(contract.output_schema.raw, base_path=contract_file)
    feedback_block = (
        _render_feedback(contract.feedback.schema, base_path=contract_file)
        if contract.feedback.supported
        else ""
    )
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


def _render_required_output(output_schema: dict, base_path: Path) -> str:
    return "\n".join(
        [
            "## Required Output",
            "```json",
            json.dumps(_expand_schema_refs(output_schema, base_path=base_path), indent=2, ensure_ascii=True),
            "```",
        ]
    )


def _render_feedback(feedback_schema: dict, base_path: Path) -> str:
    return "\n".join(
        [
            "## Feedback",
            "```json",
            json.dumps(_expand_schema_refs(feedback_schema, base_path=base_path), indent=2, ensure_ascii=True),
            "```",
        ]
    )


def _expand_schema_refs(
    schema: object,
    *,
    base_path: Path,
    document_root: object | None = None,
    seen_refs: tuple[tuple[str, str], ...] = (),
) -> object:
    if isinstance(schema, list):
        return [
            _expand_schema_refs(
                item,
                base_path=base_path,
                document_root=document_root,
                seen_refs=seen_refs,
            )
            for item in schema
        ]

    if not isinstance(schema, dict):
        return schema

    current_root = schema if document_root is None else document_root
    if "$ref" in schema:
        ref = schema["$ref"]
        resolved_schema, resolved_path, resolved_root, ref_key = _resolve_schema_ref(
            ref,
            base_path=base_path,
            document_root=current_root,
        )
        if ref_key in seen_refs:
            cycle = " -> ".join([f"{path}#{fragment}" for path, fragment in (*seen_refs, ref_key)])
            raise ValueError(f"Cyclic schema reference detected: {cycle}")

        expanded = _expand_schema_refs(
            resolved_schema,
            base_path=resolved_path,
            document_root=resolved_root,
            seen_refs=(*seen_refs, ref_key),
        )
        if not isinstance(expanded, dict):
            return expanded

        merged = dict(expanded)
        for key, value in schema.items():
            if key == "$ref":
                continue
            merged[key] = _expand_schema_refs(
                value,
                base_path=base_path,
                document_root=current_root,
                seen_refs=seen_refs,
            )
        return merged

    return {
        key: _expand_schema_refs(
            value,
            base_path=base_path,
            document_root=current_root,
            seen_refs=seen_refs,
        )
        for key, value in schema.items()
    }


def _resolve_schema_ref(
    ref: str,
    *,
    base_path: Path,
    document_root: object,
) -> tuple[object, Path, object, tuple[str, str]]:
    ref_path, _, ref_fragment = ref.partition("#")

    if ref_path:
        resolved_path = (base_path.parent / unquote(ref_path)).resolve()
        resolved_root = _load_json_file(resolved_path)
    else:
        resolved_path = base_path
        resolved_root = document_root

    resolved_schema = _resolve_json_pointer(resolved_root, ref_fragment)
    ref_key = (str(resolved_path), ref_fragment)
    return resolved_schema, resolved_path, resolved_root, ref_key


@lru_cache(maxsize=None)
def _load_json_file(path: Path) -> object:
    with path.open() as input_file:
        return json.load(input_file)


def _resolve_json_pointer(document: object, fragment: str) -> object:
    if not fragment:
        return document

    if fragment.startswith("/"):
        pointer = fragment
    elif fragment.startswith("#/"):
        pointer = fragment[1:]
    else:
        raise ValueError(f"Unsupported schema reference fragment: #{fragment}")

    current = document
    for raw_token in pointer.lstrip("/").split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
            continue
        if not isinstance(current, dict):
            raise ValueError(f"Cannot resolve schema pointer '/{pointer.lstrip('/')}'")
        current = current[token]
    return current
