from __future__ import annotations

import json
from pathlib import Path
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass

from tools.question_generator.executors import (
    ExecutorInvocationError,
    StageExecutionResult,
    extract_json_payload_text,
    validate_payload_against_output_schema,
)
from tools.question_generator.openclaw_config import (
    DEFAULT_OPENCLAW_EXECUTOR_MODE,
    OPENCLAW_RUNTIME_CONFIG_PATH_ENV_VAR,
    normalize_executor_mode,
    read_runtime_config,
    resolve_runtime_config_path,
    write_runtime_config,
)


@dataclass(frozen=True)
class OpenClawExecutorConfig:
    base_url: str
    token: str
    agent_id: str = "main"
    gateway_bin: str = "openclaw"
    runtime_config_path: str | Path | None = None
    runtime_mode: str | None = None


class _OpenClawCapabilityUnavailable(RuntimeError):
    pass


_CONNECTION_RESET_ERRNOS = {54, 104}


class OpenClawStageExecutor:
    def __init__(
        self,
        *,
        config: OpenClawExecutorConfig,
        tool_invoker=None,
        gateway_caller=None,
    ) -> None:
        self.config = config
        self._tool_invoker = tool_invoker
        self._gateway_caller = gateway_caller
        self._runtime_config_path = resolve_runtime_config_path(config.runtime_config_path)
        self._runtime_mode = read_runtime_config(
            config_path=self._runtime_config_path
        ).executor_mode
        self._runtime_mode_override = (
            normalize_executor_mode(config.runtime_mode)
            if config.runtime_mode is not None
            else None
        )

    @classmethod
    def from_env(cls) -> "OpenClawStageExecutor":
        base_url = os.environ.get("OPENCLAW_BASE_URL", "http://127.0.0.1:18789")
        token = os.environ.get("OPENCLAW_TOKEN", "")
        agent_id = os.environ.get("OPENCLAW_AGENT_ID", "main")
        gateway_bin = os.environ.get("OPENCLAW_BIN", "openclaw")
        runtime_mode = os.environ.get("OPENCLAW_EXECUTOR_MODE")
        if runtime_mode is None:
            prefer_llm_task = os.environ.get("OPENCLAW_PREFER_LLM_TASK")
            if prefer_llm_task is not None:
                runtime_mode = (
                    "llm-task" if prefer_llm_task not in {"0", "false", "False"} else "session"
                )

        runtime_config_path = os.environ.get(OPENCLAW_RUNTIME_CONFIG_PATH_ENV_VAR)
        return cls(
            config=OpenClawExecutorConfig(
                base_url=base_url,
                token=token,
                agent_id=agent_id,
                gateway_bin=gateway_bin,
                runtime_config_path=runtime_config_path,
                runtime_mode=runtime_mode,
            )
        )

    def run_stage_prompt(
        self,
        *,
        stage: str,
        prompt_text: str,
        timeout_seconds: int,
        response_schema: dict | None = None,
    ) -> StageExecutionResult:
        if response_schema is None or stage == "render":
            return self._run_plain_text_session(
                prompt_text=prompt_text,
                stage=stage,
                timeout_seconds=timeout_seconds,
            )

        executor_mode = self._resolve_executor_mode()
        if executor_mode == "llm-task":
            try:
                raw_result = self._invoke_llm_task(
                    prompt_text=prompt_text,
                    response_schema=response_schema,
                    timeout_seconds=timeout_seconds,
                )
                parsed_json = _extract_llm_task_json(raw_result)
                validate_payload_against_output_schema(parsed_json, response_schema)
                self._update_cached_executor_mode("llm-task")
                return StageExecutionResult(
                    response_text=json.dumps(parsed_json, ensure_ascii=True),
                    backend_name="openclaw-llm-task",
                    trace_text=json.dumps(raw_result, ensure_ascii=True),
                    error_text="",
                )
            except _OpenClawCapabilityUnavailable:
                self._update_cached_executor_mode("session")
            except ExecutorInvocationError:
                raise
            except Exception as exc:  # noqa: BLE001
                raise ExecutorInvocationError(
                    backend_name="openclaw-llm-task",
                    failure_reason="invalid_response",
                    message=f"OpenClaw llm-task returned invalid structured output for {stage}",
                    error_text=str(exc),
                ) from exc

        return self._run_session_json_with_repair(
            stage=stage,
            prompt_text=prompt_text,
            timeout_seconds=timeout_seconds,
            response_schema=response_schema,
        )

    def _run_plain_text_session(
        self,
        *,
        prompt_text: str,
        stage: str,
        timeout_seconds: int,
    ) -> StageExecutionResult:
        response = self._run_session_prompt(
            prompt_text=prompt_text,
            stage=stage,
            timeout_seconds=timeout_seconds,
        )
        trace_text = json.dumps(response["trace"], ensure_ascii=True)
        try:
            response_text = response["response_text"]
        except Exception as exc:  # noqa: BLE001
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="invalid_response",
                message=f"OpenClaw native session returned an invalid response shape for {stage}",
                trace_text=trace_text,
                error_text=str(exc),
            ) from exc

        return StageExecutionResult(
            response_text=response_text,
            backend_name="openclaw-session",
            trace_text=trace_text,
            error_text="",
            metadata={
                "session_key": response["session_key"],
                "gateway_run_id": response.get("run_id"),
            },
        )

    def _resolve_executor_mode(self) -> str:
        if self._runtime_mode_override is not None:
            return self._runtime_mode_override
        if self._runtime_mode:
            return self._runtime_mode
        return DEFAULT_OPENCLAW_EXECUTOR_MODE

    def _update_cached_executor_mode(self, executor_mode: str) -> None:
        mode = normalize_executor_mode(executor_mode)
        if self._runtime_mode_override is not None:
            return
        if self._runtime_mode == mode:
            return
        self._runtime_mode = mode
        try:
            write_runtime_config(
                config_path=self._runtime_config_path,
                executor_mode=mode,
            )
        except OSError:
            return

    def _run_session_json_with_repair(
        self,
        *,
        stage: str,
        prompt_text: str,
        timeout_seconds: int,
        response_schema: dict,
    ) -> StageExecutionResult:
        initial_prompt = _wrap_json_fallback_prompt(prompt_text, response_schema)
        initial_response = self._run_session_prompt(
            prompt_text=initial_prompt,
            stage=stage,
            timeout_seconds=timeout_seconds,
        )
        initial_trace = json.dumps(initial_response["trace"], ensure_ascii=True)
        try:
            initial_content = initial_response["response_text"]
        except Exception as exc:  # noqa: BLE001
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="invalid_response",
                message=f"OpenClaw native session returned an invalid response shape for {stage}",
                trace_text=initial_trace,
                error_text=str(exc),
            ) from exc
        error_message = _json_validation_error(initial_content, response_schema)
        if error_message is None:
            return StageExecutionResult(
                response_text=initial_content,
                backend_name="openclaw-session",
                trace_text=initial_trace,
                error_text="",
                metadata={
                    "session_key": initial_response["session_key"],
                    "gateway_run_id": initial_response.get("run_id"),
                },
            )

        repair_prompt = _build_repair_prompt(
            original_prompt=prompt_text,
            invalid_output=initial_content,
            error_message=error_message,
            response_schema=response_schema,
        )
        repaired_response = self._run_session_prompt(
            prompt_text=repair_prompt,
            stage=stage,
            timeout_seconds=timeout_seconds,
        )
        repaired_trace = json.dumps(repaired_response["trace"], ensure_ascii=True)
        try:
            repaired_content = repaired_response["response_text"]
        except Exception as exc:  # noqa: BLE001
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="invalid_response",
                message=f"OpenClaw native session returned an invalid repair response shape for {stage}",
                trace_text=repaired_trace,
                error_text=str(exc),
            ) from exc
        repair_error = _json_validation_error(repaired_content, response_schema)
        if repair_error is not None:
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="invalid_response",
                message=f"OpenClaw native session repair output was invalid for {stage}",
                trace_text=repaired_trace,
                error_text=repair_error,
            )
        return StageExecutionResult(
            response_text=repaired_content,
            backend_name="openclaw-session",
            trace_text=repaired_trace,
            error_text="",
            metadata={
                "session_key": repaired_response["session_key"],
                "gateway_run_id": repaired_response.get("run_id"),
            },
        )

    def _invoke_llm_task(
        self,
        *,
        prompt_text: str,
        response_schema: dict,
        timeout_seconds: int,
    ) -> dict:
        if self._tool_invoker is not None:
            result = self._tool_invoker(
                tool="llm-task",
                action="json",
                args={
                    "prompt": prompt_text,
                    "schema": response_schema,
                    "timeoutMs": timeout_seconds * 1000,
                },
            )
        else:
            result = self._invoke_tool_http(
                tool="llm-task",
                action="json",
                args={
                    "prompt": prompt_text,
                    "schema": response_schema,
                    "timeoutMs": timeout_seconds * 1000,
                },
                timeout_seconds=timeout_seconds,
            )

        if result.get("ok"):
            return result

        error = result.get("error", {})
        if result.get("status_code") == 404 or error.get("type") == "not_found":
            raise _OpenClawCapabilityUnavailable("llm-task unavailable")

        raise ExecutorInvocationError(
            backend_name="openclaw-llm-task",
            failure_reason="tool_error",
            message=f"OpenClaw llm-task failed: {error.get('message', 'unknown error')}",
            trace_text=json.dumps(result, ensure_ascii=True),
            error_text=json.dumps(error, ensure_ascii=True),
        )

    def _run_session_prompt(
        self,
        *,
        prompt_text: str,
        stage: str,
        timeout_seconds: int,
    ) -> dict:
        session_key = _build_session_key(agent_id=self.config.agent_id, stage=stage)
        send_result = self._call_gateway(
            method="chat.send",
            params={
                "sessionKey": session_key,
                "message": prompt_text,
                "idempotencyKey": uuid.uuid4().hex,
            },
            timeout_seconds=timeout_seconds,
        )
        run_id = _extract_gateway_run_id(send_result)
        deadline = time.monotonic() + timeout_seconds
        last_history = None
        while time.monotonic() < deadline:
            last_history = self._call_gateway(
                method="chat.history",
                params={"sessionKey": session_key},
                timeout_seconds=max(1, min(timeout_seconds, int(deadline - time.monotonic()) or 1)),
            )
            response_text = _extract_history_response_text(last_history)
            if response_text is not None:
                return {
                    "session_key": session_key,
                    "run_id": run_id,
                    "response_text": response_text,
                    "trace": {
                        "send": send_result,
                        "history": last_history,
                        "session_key": session_key,
                        "run_id": run_id,
                    },
                }
            time.sleep(0.25)

        raise ExecutorInvocationError(
            backend_name="openclaw-session",
            failure_reason="timeout",
            message=f"OpenClaw native session timed out for {stage}",
            trace_text=json.dumps(
                {
                    "send": send_result,
                    "history": last_history,
                    "session_key": session_key,
                    "run_id": run_id,
                },
                ensure_ascii=True,
            ),
            error_text="Timed out waiting for an assistant message in chat.history",
        )

    def _call_gateway(
        self,
        *,
        method: str,
        params: dict,
        timeout_seconds: int,
    ) -> dict:
        if self._gateway_caller is not None:
            return self._gateway_caller(
                method=method,
                params=params,
                timeout_seconds=timeout_seconds,
            )
        return self._call_gateway_cli(
            method=method,
            params=params,
            timeout_seconds=timeout_seconds,
        )

    def _call_gateway_cli(
        self,
        *,
        method: str,
        params: dict,
        timeout_seconds: int,
    ) -> dict:
        command = [
            self.config.gateway_bin,
            "gateway",
            "call",
            method,
            "--params",
            json.dumps(params, ensure_ascii=True),
            "--json",
        ]
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="transport_error",
                message=f"OpenClaw CLI not found while calling native gateway method {method}",
                error_text=str(exc),
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="timeout",
                message=f"OpenClaw native gateway call timed out for {method}",
                trace_text=_coerce_subprocess_text(exc.stdout),
                error_text=_coerce_subprocess_text(exc.stderr),
            ) from exc

        if completed.returncode != 0:
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="transport_error",
                message=f"OpenClaw native gateway call failed for {method}",
                trace_text=completed.stdout,
                error_text=completed.stderr,
            )
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ExecutorInvocationError(
                backend_name="openclaw-session",
                failure_reason="invalid_response",
                message=f"OpenClaw native gateway call returned invalid JSON for {method}",
                trace_text=completed.stdout,
                error_text=str(exc),
            ) from exc

    def _invoke_tool_http(
        self,
        *,
        tool: str,
        action: str,
        args: dict,
        timeout_seconds: int,
    ) -> dict:
        payload = {
            "tool": tool,
            "action": action,
            "args": args,
        }
        request = urllib.request.Request(
            f"{self.config.base_url.rstrip('/')}/tools/invoke",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.token}",
            },
            method="POST",
        )
        for attempt in range(2):
            try:
                with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(body)
                except json.JSONDecodeError:
                    parsed = {"ok": False, "error": {"type": "http_error", "message": body}}
                parsed["status_code"] = exc.code
                return parsed
            except urllib.error.URLError as exc:
                if attempt == 0 and _is_connection_reset_error(exc):
                    continue
                raise ExecutorInvocationError(
                    backend_name="openclaw-llm-task",
                    failure_reason="transport_error",
                    message="OpenClaw llm-task request failed",
                    error_text=str(exc),
                ) from exc
            except OSError as exc:
                if attempt == 0 and _is_connection_reset_error(exc):
                    continue
                raise ExecutorInvocationError(
                    backend_name="openclaw-llm-task",
                    failure_reason="transport_error",
                    message="OpenClaw llm-task request failed",
                    error_text=str(exc),
                ) from exc
            except json.JSONDecodeError as exc:
                raise ExecutorInvocationError(
                    backend_name="openclaw-llm-task",
                    failure_reason="invalid_response",
                    message="OpenClaw llm-task returned invalid JSON envelope",
                    error_text=str(exc),
                ) from exc


def _extract_llm_task_json(raw_result: dict) -> dict:
    result = raw_result.get("result", {})
    if isinstance(result.get("details"), dict) and isinstance(result["details"].get("json"), dict):
        return result["details"]["json"]
    if isinstance(result.get("json"), dict):
        return result["json"]
    if isinstance(raw_result.get("json"), dict):
        return raw_result["json"]
    raise ValueError("OpenClaw llm-task response did not include parsed JSON details")


def _is_connection_reset_error(exc: BaseException) -> bool:
    if isinstance(exc, urllib.error.URLError) and exc.reason is not None:
        return _is_connection_reset_error(exc.reason)
    if isinstance(exc, ConnectionResetError):
        return True
    errno_value = getattr(exc, "errno", None)
    if errno_value in _CONNECTION_RESET_ERRNOS:
        return True
    return "connection reset by peer" in str(exc).lower()


def _build_session_key(*, agent_id: str, stage: str) -> str:
    return f"agent:{agent_id}:deep-think:{stage}:{uuid.uuid4().hex[:12]}"


def _extract_gateway_run_id(raw_result: dict) -> str | None:
    payload = _extract_gateway_payload(raw_result)
    for key in ("runId", "run_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _extract_gateway_payload(raw_result: dict) -> dict:
    payload = raw_result.get("result")
    if isinstance(payload, dict):
        return payload
    return raw_result


def _extract_history_response_text(raw_result: dict) -> str | None:
    payload = _extract_gateway_payload(raw_result)
    for key in ("messages", "history", "items"):
        messages = payload.get(key)
        if isinstance(messages, list):
            for message in reversed(messages):
                if not isinstance(message, dict):
                    continue
                role = str(message.get("role") or message.get("kind") or message.get("type") or "").lower()
                if role not in {"assistant", "model"}:
                    continue
                text = _extract_message_text(message)
                if text.strip():
                    return text
            return None
    return None


def _extract_message_text(message: dict) -> str:
    for key in ("content", "text", "message"):
        value = message.get(key)
        text = _coerce_message_text(value)
        if text is not None:
            return text
    return ""


def _coerce_message_text(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "content", "value"):
            nested = value.get(key)
            if isinstance(nested, str):
                return nested
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
                continue
            if not isinstance(item, dict):
                continue
            item_type = str(item.get("type") or "").lower()
            if item_type in {"text", "output_text"}:
                part = item.get("text") or item.get("content") or item.get("value")
                if isinstance(part, str):
                    parts.append(part)
        if parts:
            return "".join(parts)
    return None


def _coerce_subprocess_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _wrap_json_fallback_prompt(prompt_text: str, response_schema: dict) -> str:
    return "\n\n".join(
        [
            "JSON fallback contract:",
            "Return exactly one JSON object.",
            "Do not include markdown fences.",
            "Any non-JSON output will be rejected and repaired.",
            "Required output schema:",
            json.dumps(response_schema, indent=2, ensure_ascii=True),
            prompt_text,
        ]
    )


def _build_repair_prompt(
    *,
    original_prompt: str,
    invalid_output: str,
    error_message: str,
    response_schema: dict,
) -> str:
    return "\n\n".join(
        [
            "Repair the previous response.",
            "Return exactly one corrected JSON object and nothing else.",
            "The previous response was rejected.",
            f"Validation error: {error_message}",
            "Required output schema:",
            json.dumps(response_schema, indent=2, ensure_ascii=True),
            "Previous invalid output:",
            invalid_output,
            "Original task prompt:",
            original_prompt,
        ]
    )


def _json_validation_error(response_text: str, response_schema: dict) -> str | None:
    try:
        payload = extract_json_payload_text(response_text)
        validate_payload_against_output_schema(payload, response_schema)
    except Exception as exc:  # noqa: BLE001
        return str(exc)
    return None
