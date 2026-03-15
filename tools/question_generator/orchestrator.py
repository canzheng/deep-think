from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from shutil import copyfile

from tools.question_generator.assembler import _expand_schema_refs, assemble_stage_prompt
from tools.question_generator.bootstrap import bootstrap_topic_state
from tools.question_generator.contracts import load_contract
from tools.question_generator.pathing import contract_path, normalize_stage_name, repo_root, stage_stub


MANIFEST_FILENAME = "run_manifest.json"
SHARED_STATE_FILENAME = "shared_state.json"
STAGES_DIRNAME = "stages"
PROMPT_FILENAME = "prompt.md"
RESPONSE_RAW_FILENAME = "response.raw.md"
RESPONSE_PARSED_FILENAME = "response.parsed.json"
RESPONSE_SCHEMA_FILENAME = "response.schema.json"
CODEX_STDOUT_FILENAME = "codex.stdout.jsonl"
CODEX_STDERR_FILENAME = "codex.stderr.txt"
STAGE_RECORD_FILENAME = "stage.json"
ANSWERING_MODEL = "gpt-5.4"
ANSWERING_REASONING_EFFORT = "high"
DEFAULT_CODEX_BIN = "codex"
DEFAULT_TIMEOUT_SECONDS = 500


def load_recipe(recipe_path: Path) -> dict:
    with recipe_path.open() as recipe_file:
        recipe = json.load(recipe_file)

    if not isinstance(recipe, dict):
        raise ValueError("Recipe must be a JSON object")
    stages = recipe.get("stages")
    if not isinstance(stages, list) or not stages:
        raise ValueError("Recipe must define a non-empty 'stages' list")

    for item in stages:
        if not isinstance(item, dict) or "stage" not in item:
            raise ValueError("Each recipe stage entry must be an object with a 'stage' field")

    return recipe


def initialize_run(
    *,
    state_path: Path,
    output_dir: Path,
    run_id: str,
) -> Path:
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / STAGES_DIRNAME).mkdir(parents=True, exist_ok=True)

    shared_state_path = run_dir / SHARED_STATE_FILENAME
    copyfile(state_path, shared_state_path)

    manifest = {
        "run_id": run_id,
        "created_at": _timestamp(),
        "state_path": str(shared_state_path),
        "stages": {},
    }
    _write_json(run_dir / MANIFEST_FILENAME, manifest)
    return run_dir


def initialize_topic_run(
    *,
    topic: str,
    output_dir: Path,
    run_id: str,
) -> Path:
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / STAGES_DIRNAME).mkdir(parents=True, exist_ok=True)

    shared_state_path = run_dir / SHARED_STATE_FILENAME
    _write_json(shared_state_path, bootstrap_topic_state(topic))

    manifest = {
        "run_id": run_id,
        "created_at": _timestamp(),
        "state_path": str(shared_state_path),
        "stages": {},
    }
    _write_json(run_dir / MANIFEST_FILENAME, manifest)
    return run_dir


def load_run_manifest(run_dir: Path) -> dict:
    with (run_dir / MANIFEST_FILENAME).open() as manifest_file:
        return json.load(manifest_file)


def prepare_stage(
    run_dir: Path,
    stage: str,
    *,
    optional_reads: list[str] | None = None,
) -> dict:
    normalized_stage = normalize_stage_name(stage)
    stage_dir = _stage_dir(run_dir, normalized_stage)
    stage_dir.mkdir(parents=True, exist_ok=True)

    state = _load_shared_state(run_dir)
    prompt = assemble_stage_prompt(
        normalized_stage,
        state,
        optional_reads=optional_reads,
    )
    prompt_path = stage_dir / PROMPT_FILENAME
    prompt_path.write_text(prompt, encoding="utf-8")
    record = {
        "stage": normalized_stage,
        "status": "prompt_prepared",
        "prepared_at": _timestamp(),
        "prompt_path": str(prompt_path),
        "optional_reads": optional_reads or [],
        "writes": load_contract(normalized_stage).writes,
    }
    if normalized_stage != "render":
        response_schema_path = stage_dir / RESPONSE_SCHEMA_FILENAME
        _write_json(response_schema_path, build_stage_response_schema(normalized_stage))
        record["response_schema_path"] = str(response_schema_path)
    _write_stage_record(run_dir, normalized_stage, record)
    return record


def apply_stage_response(
    run_dir: Path,
    stage: str,
    *,
    response_text: str | None = None,
    response_path: Path | None = None,
) -> dict:
    normalized_stage = normalize_stage_name(stage)
    if response_text is None:
        if response_path is None:
            raise ValueError("Either response_text or response_path is required")
        response_text = response_path.read_text(encoding="utf-8")

    stage_dir = _stage_dir(run_dir, normalized_stage)
    stage_dir.mkdir(parents=True, exist_ok=True)
    raw_path = stage_dir / RESPONSE_RAW_FILENAME
    raw_path.write_text(response_text, encoding="utf-8")
    contract = load_contract(normalized_stage)
    prior_record = _load_stage_record(run_dir, normalized_stage)
    if normalized_stage == "render":
        record = {
            **prior_record,
            "stage": normalized_stage,
            "status": "response_applied",
            "response_applied_at": _timestamp(),
            "response_raw_path": str(raw_path),
            "merged_sections": contract.writes,
        }
        _write_stage_record(run_dir, normalized_stage, record)
        return record

    parsed_path = stage_dir / RESPONSE_PARSED_FILENAME
    parsed_payload = extract_json_payload(response_text)
    _validate_stage_payload(contract, parsed_payload)
    _merge_stage_payload(run_dir, contract.writes, parsed_payload)
    _write_json(parsed_path, parsed_payload)

    record = {
        **prior_record,
        "stage": normalized_stage,
        "status": "response_applied",
        "response_applied_at": _timestamp(),
        "response_raw_path": str(raw_path),
        "response_parsed_path": str(parsed_path),
        "merged_sections": contract.writes,
    }
    _write_stage_record(run_dir, normalized_stage, record)
    return record


def build_stage_response_schema(stage: str) -> dict:
    normalized_stage = normalize_stage_name(stage)
    contract = load_contract(normalized_stage)
    expanded = _expand_schema_refs(
        contract.output_schema.raw,
        base_path=contract_path(normalized_stage),
    )
    if not isinstance(expanded, dict):
        raise ValueError(f"Expanded output schema for {normalized_stage} must be an object")

    if contract.feedback.supported and contract.feedback.field and contract.feedback.schema is not None:
        properties = dict(expanded.get("properties", {}))
        properties[contract.feedback.field] = _infer_schema_from_example(contract.feedback.schema)
        expanded = dict(expanded)
        expanded["properties"] = properties
        expanded.setdefault("additionalProperties", False)

    transformed = _to_codex_output_schema(expanded)
    if not isinstance(transformed, dict):
        raise ValueError(f"Codex output schema for {normalized_stage} must be an object")
    return transformed


def build_codex_exec_command(
    *,
    stage: str,
    codex_bin: str,
    workspace_dir: Path,
    response_schema_path: Path,
    response_raw_path: Path,
) -> list[str]:
    command = [
        codex_bin,
        "exec",
        "--ephemeral",
        "-m",
        ANSWERING_MODEL,
        "-c",
        f'reasoning_effort="{ANSWERING_REASONING_EFFORT}"',
        "-s",
        "read-only",
        "-C",
        str(workspace_dir),
    ]
    if normalize_stage_name(stage) != "render":
        command.extend(
            [
                "--output-schema",
                str(response_schema_path),
                "--json",
            ]
        )
    command.extend(
        [
            "-o",
            str(response_raw_path),
            "-",
        ]
    )
    return command


def build_stage_agent_prompt(stage: str, stage_prompt: str) -> str:
    instructions = [
        "You are the answering model for one question-generator workflow stage.",
        "Do not run shell commands.",
        "Do not inspect files.",
        "Do not browse project context beyond the prompt you were given.",
        "Do not use tools.",
    ]
    if normalize_stage_name(stage) == "render":
        instructions.append("Return the final deliverable directly as plain text.")
    else:
        instructions.extend(
            [
                "Return exactly one JSON object matching the provided schema.",
                "Do not include markdown fences or explanatory prose.",
                "If a secondary classification or rationale is not needed, use null.",
            ]
        )
    instructions.append(stage_prompt)
    return "\n\n".join(instructions)


def run_stage(
    run_dir: Path,
    stage: str,
    *,
    optional_reads: list[str] | None = None,
    codex_bin: str = DEFAULT_CODEX_BIN,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    workspace_dir: Path | None = None,
) -> dict:
    normalized_stage = normalize_stage_name(stage)
    prepared = prepare_stage(run_dir, normalized_stage, optional_reads=optional_reads)
    stage_dir = _stage_dir(run_dir, normalized_stage)
    prompt_path = Path(prepared["prompt_path"])
    response_raw_path = stage_dir / RESPONSE_RAW_FILENAME
    stdout_path = stage_dir / CODEX_STDOUT_FILENAME
    stderr_path = stage_dir / CODEX_STDERR_FILENAME
    workspace = repo_root() if workspace_dir is None else workspace_dir
    command = build_codex_exec_command(
        stage=normalized_stage,
        codex_bin=codex_bin,
        workspace_dir=workspace,
        response_schema_path=Path(prepared.get("response_schema_path", stage_dir / RESPONSE_SCHEMA_FILENAME)),
        response_raw_path=response_raw_path,
    )

    try:
        completed = subprocess.run(
            command,
            input=build_stage_agent_prompt(normalized_stage, prompt_path.read_text(encoding="utf-8")),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout_path.write_text(_coerce_text(exc.stdout), encoding="utf-8")
        stderr_path.write_text(_coerce_text(exc.stderr), encoding="utf-8")
        record = {
            **prepared,
            "status": "codex_failed",
            "model": ANSWERING_MODEL,
            "reasoning_effort": ANSWERING_REASONING_EFFORT,
            "ephemeral": True,
            "timeout_seconds": timeout_seconds,
            "codex_command": command,
            "codex_stdout_path": str(stdout_path),
            "codex_stderr_path": str(stderr_path),
            "failure_reason": "timeout",
        }
        _write_stage_record(run_dir, normalized_stage, record)
        raise RuntimeError(f"Codex stage invocation timed out for {normalized_stage}") from exc

    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    record = {
        **prepared,
        "model": ANSWERING_MODEL,
        "reasoning_effort": ANSWERING_REASONING_EFFORT,
        "ephemeral": True,
        "timeout_seconds": timeout_seconds,
        "codex_command": command,
        "codex_stdout_path": str(stdout_path),
        "codex_stderr_path": str(stderr_path),
    }

    if completed.returncode != 0 or not response_raw_path.is_file():
        record["status"] = "codex_failed"
        record["failure_reason"] = "non_zero_exit" if completed.returncode != 0 else "missing_response"
        record["codex_returncode"] = completed.returncode
        _write_stage_record(run_dir, normalized_stage, record)
        raise RuntimeError(
            f"Codex stage invocation failed for {normalized_stage}: {completed.stderr.strip() or 'missing response'}"
        )

    record["status"] = "codex_completed"
    record["codex_returncode"] = completed.returncode
    _write_stage_record(run_dir, normalized_stage, record)
    return apply_stage_response(
        run_dir,
        normalized_stage,
        response_path=response_raw_path,
    )


def run_recipe(
    *,
    recipe_path: Path,
    state_path: Path,
    output_dir: Path,
    run_id: str,
    codex_bin: str = DEFAULT_CODEX_BIN,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    workspace_dir: Path | None = None,
) -> dict:
    run_dir = initialize_run(
        state_path=state_path,
        output_dir=output_dir,
        run_id=run_id,
    )

    return run_recipe_on_run(
        recipe_path=recipe_path,
        run_dir=run_dir,
        codex_bin=codex_bin,
        timeout_seconds=timeout_seconds,
        workspace_dir=workspace_dir,
    )


def run_recipe_on_run(
    *,
    recipe_path: Path,
    run_dir: Path,
    start_stage: str | None = None,
    stop_stage: str | None = None,
    codex_bin: str = DEFAULT_CODEX_BIN,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    workspace_dir: Path | None = None,
) -> dict:
    recipe = load_recipe(recipe_path)
    selected_items = _select_recipe_items(
        recipe["stages"],
        start_stage=start_stage,
        stop_stage=stop_stage,
    )

    stage_results = []
    for item in selected_items:
        stage_results.append(
            run_stage(
                run_dir,
                item["stage"],
                optional_reads=item.get("optional_reads", []),
                codex_bin=codex_bin,
                timeout_seconds=timeout_seconds,
                workspace_dir=workspace_dir,
            )
        )

    manifest = load_run_manifest(run_dir)
    manifest["recipe"] = {
        "path": str(recipe_path),
        "name": recipe.get("name", ""),
    }
    _write_json(run_dir / MANIFEST_FILENAME, manifest)
    return {
        "run_dir": str(run_dir),
        "recipe_name": recipe.get("name", ""),
        "stages": stage_results,
    }


def run_topic(
    *,
    topic: str,
    recipe_path: Path,
    output_dir: Path,
    run_id: str,
    pause_after_stage: str | None = None,
    codex_bin: str = DEFAULT_CODEX_BIN,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    workspace_dir: Path | None = None,
) -> dict:
    run_dir = initialize_topic_run(
        topic=topic,
        output_dir=output_dir,
        run_id=run_id,
    )

    return run_recipe_on_run(
        recipe_path=recipe_path,
        run_dir=run_dir,
        stop_stage=pause_after_stage,
        codex_bin=codex_bin,
        timeout_seconds=timeout_seconds,
        workspace_dir=workspace_dir,
    )


def update_routing(run_dir: Path, patch: dict) -> dict:
    if not isinstance(patch, dict) or not patch:
        raise ValueError("Routing patch must be a non-empty JSON object")

    state = _load_shared_state(run_dir)
    if "routing" not in state or not isinstance(state["routing"], dict):
        raise ValueError("Routing cannot be updated before the routing stage has populated it")

    merged_routing = _deep_merge_dicts(state["routing"], patch)
    state["routing"] = merged_routing
    _write_json(run_dir / SHARED_STATE_FILENAME, state)
    return merged_routing


def extract_json_payload(response_text: str) -> dict:
    stripped = response_text.strip()
    direct = _try_json_loads(stripped)
    if isinstance(direct, dict):
        return direct

    fence_pattern = re.compile(
        r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```",
        re.DOTALL,
    )
    for match in fence_pattern.finditer(response_text):
        candidate = _try_json_loads(match.group(1).strip())
        if isinstance(candidate, dict):
            return candidate

    first_brace = response_text.find("{")
    last_brace = response_text.rfind("}")
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        candidate = _try_json_loads(response_text[first_brace : last_brace + 1])
        if isinstance(candidate, dict):
            return candidate

    raise ValueError("Could not parse a JSON object from the stage response")


def _validate_stage_payload(contract, payload: dict) -> None:
    required_keys = set(contract.output_schema.required)
    missing = required_keys - set(payload)
    if missing:
        raise ValueError(f"Stage payload is missing required keys: {sorted(missing)}")

    allowed_keys = set(contract.output_schema.properties)
    if contract.feedback.supported and contract.feedback.field:
        allowed_keys.add(contract.feedback.field)
    unexpected = set(payload) - allowed_keys
    if unexpected:
        raise ValueError(f"Stage payload includes unexpected keys: {sorted(unexpected)}")


def _merge_stage_payload(run_dir: Path, writes: list[str], payload: dict) -> None:
    if not writes:
        return

    state = _load_shared_state(run_dir)
    for key in writes:
        state[key] = payload[key]
    _write_json(run_dir / SHARED_STATE_FILENAME, state)


def _write_stage_record(run_dir: Path, stage: str, record: dict) -> None:
    stage_dir = _stage_dir(run_dir, stage)
    stage_dir.mkdir(parents=True, exist_ok=True)
    _write_json(stage_dir / STAGE_RECORD_FILENAME, record)

    manifest = load_run_manifest(run_dir)
    manifest.setdefault("stages", {})[stage] = record
    _write_json(run_dir / MANIFEST_FILENAME, manifest)


def _load_stage_record(run_dir: Path, stage: str) -> dict:
    stage_record_path = _stage_dir(run_dir, stage) / STAGE_RECORD_FILENAME
    if not stage_record_path.is_file():
        return {}
    with stage_record_path.open() as stage_record_file:
        return json.load(stage_record_file)


def _load_shared_state(run_dir: Path) -> dict:
    with (run_dir / SHARED_STATE_FILENAME).open() as state_file:
        return json.load(state_file)


def _stage_dir(run_dir: Path, stage: str) -> Path:
    return run_dir / STAGES_DIRNAME / stage_stub(stage)


def _select_recipe_items(
    items: list[dict],
    *,
    start_stage: str | None = None,
    stop_stage: str | None = None,
) -> list[dict]:
    normalized_start = normalize_stage_name(start_stage) if start_stage else None
    normalized_stop = normalize_stage_name(stop_stage) if stop_stage else None

    available_stages = [normalize_stage_name(item["stage"]) for item in items]
    if normalized_start and normalized_start not in available_stages:
        raise ValueError(f"Unknown start stage {start_stage!r} for recipe")
    if normalized_stop and normalized_stop not in available_stages:
        raise ValueError(f"Unknown stop stage {stop_stage!r} for recipe")

    selected: list[dict] = []
    started = normalized_start is None
    for item in items:
        normalized_stage = normalize_stage_name(item["stage"])
        if not started and normalized_stage == normalized_start:
            started = True
        if not started:
            continue

        selected.append(item)
        if normalized_stop and normalized_stage == normalized_stop:
            break

    return selected


def _deep_merge_dicts(existing: dict, patch: dict) -> dict:
    merged = dict(existing)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(existing.get(key), dict):
            merged[key] = _deep_merge_dicts(existing[key], value)
            continue
        merged[key] = value
    return merged


def _try_json_loads(value: str) -> object | None:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _infer_schema_from_example(value: object) -> dict:
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, list):
        if value:
            return {
                "type": "array",
                "items": _infer_schema_from_example(value[0]),
            }
        return {"type": "array"}
    if isinstance(value, dict):
        return {
            "type": "object",
            "properties": {
                key: _infer_schema_from_example(item)
                for key, item in value.items()
            },
            "required": list(value.keys()),
            "additionalProperties": False,
        }
    return {}


def _to_codex_output_schema(schema: object, *, optional: bool = False) -> object:
    if isinstance(schema, list):
        return [_to_codex_output_schema(item) for item in schema]

    if not isinstance(schema, dict):
        return schema

    transformed = {
        key: _to_codex_output_schema(value)
        for key, value in schema.items()
        if key not in {"$schema", "$id", "title", "default"}
    }

    if transformed.get("type") == "object" and "properties" in transformed:
        properties = {
            key: _to_codex_output_schema(value, optional=key not in set(transformed.get("required", [])))
            for key, value in transformed["properties"].items()
        }
        transformed["properties"] = properties
        transformed["required"] = list(properties.keys())
        transformed["additionalProperties"] = False
        return _make_nullable(transformed) if optional else transformed

    if transformed.get("type") == "array" and "items" in transformed:
        transformed["items"] = _to_codex_output_schema(transformed["items"])
        return _make_nullable(transformed) if optional else transformed

    if "anyOf" in transformed:
        any_of = transformed["anyOf"]
        if optional and isinstance(any_of, list):
            has_null = any(
                isinstance(item, dict) and item.get("type") == "null"
                for item in any_of
            )
            if not has_null:
                transformed["anyOf"] = [*any_of, {"type": "null"}]
        return transformed

    return _make_nullable(transformed) if optional else transformed


def _make_nullable(schema: dict) -> dict:
    transformed = dict(schema)
    schema_type = transformed.get("type")
    if isinstance(schema_type, str):
        transformed["type"] = [schema_type, "null"]
    elif isinstance(schema_type, list):
        if "null" not in schema_type:
            transformed["type"] = [*schema_type, "null"]
    else:
        transformed = {
            "anyOf": [
                transformed,
                {"type": "null"},
            ]
        }

    if "enum" in transformed and None not in transformed["enum"]:
        transformed["enum"] = [*transformed["enum"], None]
    return transformed


def _coerce_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        return value
    return str(value)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
