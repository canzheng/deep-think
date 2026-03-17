from __future__ import annotations

import copy
import json
import re
from functools import lru_cache
from urllib.parse import unquote

import chevron

from tools.question_generator.adapter_rendering import build_stage_guidance
from tools.question_generator.adapter_resolution import resolve_stage_modules
from tools.question_generator.contracts import load_contract
from tools.question_generator.pathing import contract_path, normalize_stage_name, stage_template_path
from tools.question_generator.render_context import (
    build_render_context,
    render_wrapper_template,
    select_render_template,
)


def assemble_stage_prompt(
    stage: str,
    state: dict,
    optional_reads: list[str] | None = None,
    run_manifest: dict | None = None,
) -> str:
    normalized_stage = normalize_stage_name(stage)
    if normalized_stage != "render":
        return _assemble_non_render_stage_prompt(stage, state)

    return _assemble_render_stage_prompt(stage, state, run_manifest=run_manifest)


def _assemble_non_render_stage_prompt(stage: str, state: dict) -> str:
    contract_file = contract_path(stage)
    contract = load_contract(stage)
    template = stage_template_path(stage).read_text().strip()
    modules = resolve_stage_modules(contract, state.get("routing", {}))
    context = _build_non_render_context(
        stage=stage,
        state=state,
        stage_guidance=build_stage_guidance(stage, modules) if modules else {"required": [], "conditional": []},
        required_output_schema=_render_schema_block(contract.output_schema.raw, base_path=contract_file),
        feedback_schema=(
            _render_schema_block(contract.feedback.schema, base_path=contract_file)
            if contract.feedback.supported
            else ""
        ),
    )
    return chevron.render(template, context).strip()


def _assemble_render_stage_prompt(
    stage: str,
    state: dict,
    *,
    run_manifest: dict | None = None,
) -> str:
    contract_file = contract_path(stage)
    contract = load_contract(stage)
    modules = resolve_stage_modules(contract, state.get("routing", {}))
    stage_guidance = build_stage_guidance(stage, modules) if modules else {"required": [], "conditional": []}
    context = build_render_context(
        state,
        stage_guidance=stage_guidance,
        required_output_schema=_render_schema_block(contract.output_schema.raw, base_path=contract_file),
        feedback_schema=(
            _render_schema_block(contract.feedback.schema, base_path=contract_file)
            if contract.feedback.supported
            else ""
        ),
        run_manifest=run_manifest,
    )
    body_template = select_render_template(state["routing"]["output_mode"]).read_text().strip()
    wrapper_template = render_wrapper_template().read_text().strip()
    context["topic"] = _render_topic_block(state.get("topic", ""))
    context["render_body"] = chevron.render(body_template, context).strip()
    return chevron.render(wrapper_template, context).strip()


def _build_non_render_context(
    *,
    stage: str,
    state: dict,
    stage_guidance: dict[str, list[dict[str, str]]],
    required_output_schema: str,
    feedback_schema: str,
) -> dict[str, object]:
    context = copy.deepcopy(state)
    context["topic"] = _render_topic_block(state.get("topic", ""))
    context["stage_guidance"] = copy.deepcopy(stage_guidance)
    context["required_output_schema"] = required_output_schema
    context["feedback_schema"] = feedback_schema
    context["stage"] = normalize_stage_name(stage)
    return context


def _render_topic_block(topic: str) -> str:
    if not topic:
        return ""

    backtick_runs = [len(match.group(0)) for match in re.finditer(r"`+", topic)]
    fence = "`" * max(3, max(backtick_runs, default=0) + 1)
    return "\n".join([f"{fence}text", topic, fence])

def _render_schema_block(schema: dict, *, base_path: Path) -> str:
    return "\n".join(
        [
            "```json",
            json.dumps(_expand_schema_refs(schema, base_path=base_path), indent=2, ensure_ascii=True),
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
