from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


ANSWERING_MODEL = "gpt-5.4"
ANSWERING_REASONING_EFFORT = "high"


@dataclass(frozen=True)
class StageExecutionResult:
    response_text: str
    backend_name: str
    trace_text: str | None = None
    error_text: str | None = None
    metadata: dict[str, object] | None = None


class StageExecutor(Protocol):
    def run_stage_prompt(
        self,
        *,
        stage: str,
        prompt_text: str,
        timeout_seconds: int,
        response_schema: dict | None = None,
    ) -> StageExecutionResult: ...


@dataclass(frozen=True)
class ExecutorInvocationError(RuntimeError):
    backend_name: str
    failure_reason: str
    message: str
    trace_text: str | None = None
    error_text: str | None = None
    metadata: dict[str, object] | None = None

    def __str__(self) -> str:
        return self.message


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
    if stage != "render":
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


@dataclass
class CodexStageExecutor:
    codex_bin: str
    workspace_dir: Path
    response_schema_dir: Path

    def run_stage_prompt(
        self,
        *,
        stage: str,
        prompt_text: str,
        timeout_seconds: int,
        response_schema: dict | None = None,
    ) -> StageExecutionResult:
        with tempfile.TemporaryDirectory(dir=self.response_schema_dir) as temp_dir:
            temp_root = Path(temp_dir)
            response_raw_path = temp_root / f"{stage}.response.md"
            response_schema_path = temp_root / f"{stage}.schema.json"
            if response_schema is not None:
                response_schema_path.write_text(
                    json.dumps(response_schema, indent=2, ensure_ascii=True),
                    encoding="utf-8",
                )

            command = build_codex_exec_command(
                stage=stage,
                codex_bin=self.codex_bin,
                workspace_dir=self.workspace_dir,
                response_schema_path=response_schema_path,
                response_raw_path=response_raw_path,
            )

            try:
                completed = subprocess.run(
                    command,
                    input=prompt_text,
                    text=True,
                    capture_output=True,
                    timeout=timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise ExecutorInvocationError(
                    backend_name="codex",
                    failure_reason="timeout",
                    message=f"Codex stage invocation timed out for {stage}",
                    trace_text=_coerce_text(exc.stdout),
                    error_text=_coerce_text(exc.stderr),
                    metadata={
                        "model": ANSWERING_MODEL,
                        "reasoning_effort": ANSWERING_REASONING_EFFORT,
                        "ephemeral": True,
                        "command": command,
                    },
                ) from exc

            trace_text = completed.stdout
            error_text = completed.stderr
            metadata = {
                "model": ANSWERING_MODEL,
                "reasoning_effort": ANSWERING_REASONING_EFFORT,
                "ephemeral": True,
                "command": command,
                "returncode": completed.returncode,
            }

            if completed.returncode != 0 or not response_raw_path.is_file():
                raise ExecutorInvocationError(
                    backend_name="codex",
                    failure_reason="non_zero_exit" if completed.returncode != 0 else "missing_response",
                    message=f"Codex stage invocation failed for {stage}: {completed.stderr.strip() or 'missing response'}",
                    trace_text=trace_text,
                    error_text=error_text,
                    metadata=metadata,
                )

            response_text = response_raw_path.read_text(encoding="utf-8")
            return StageExecutionResult(
                response_text=response_text,
                backend_name="codex",
                trace_text=trace_text,
                error_text=error_text,
                metadata=metadata,
            )


def extract_json_payload_text(response_text: str) -> dict:
    stripped = response_text.strip()
    direct = _try_json_loads(stripped)
    if isinstance(direct, dict):
        return direct

    import re

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


def validate_payload_against_output_schema(
    payload: dict,
    output_schema: dict | None,
) -> None:
    if output_schema is None:
        return

    required = set(output_schema.get("required", []))
    missing = required - set(payload)
    if missing:
        raise ValueError(f"Stage payload is missing required keys: {sorted(missing)}")

    allowed = set(output_schema.get("properties", {}).keys())
    unexpected = set(payload) - allowed
    if unexpected:
        raise ValueError(f"Stage payload includes unexpected keys: {sorted(unexpected)}")


def _try_json_loads(value: str) -> object | None:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _coerce_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
