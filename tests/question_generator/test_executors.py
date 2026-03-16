import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch


from tools.question_generator.executors import ExecutorInvocationError, StageExecutionResult
from tools.question_generator.openclaw_config import (
    read_runtime_config,
    write_runtime_config,
)
from tools.question_generator.openclaw_executor import (
    OpenClawExecutorConfig,
    OpenClawStageExecutor,
)


class OpenClawExecutorTest(unittest.TestCase):
    class _FakeHttpResponse:
        def __init__(self, payload: dict):
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(self._payload).encode("utf-8")

    def test_openclaw_runtime_config_defaults_to_auto_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            runtime_config = read_runtime_config(config_path=config_path)

            self.assertEqual(runtime_config.executor_mode, "auto")

    def test_openclaw_auto_mode_persists_llm_task_after_success(self) -> None:
        calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            calls.append(f"tool:{tool}:{action}")
            return {
                "ok": True,
                "result": {
                    "details": {
                        "json": {"routing": {"task": "Decide"}}
                    }
                },
            }

        def fake_chat_completion(**kwargs):
            self.fail("chat should not be used when llm-task succeeds")

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="routing",
                prompt_text="Stage prompt",
                timeout_seconds=30,
                response_schema={
                    "type": "object",
                    "required": ["routing"],
                    "properties": {"routing": {"type": "object"}},
                },
            )

            self.assertEqual(calls, ["tool:llm-task:json"])
            self.assertEqual(result.backend_name, "openclaw-llm-task")
            self.assertEqual(
                read_runtime_config(config_path=config_path).executor_mode,
                "llm-task",
            )

    def test_openclaw_auto_mode_persists_chat_fallback_after_not_found(self) -> None:
        tool_calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            tool_calls.append(f"tool:{tool}:{action}")
            return {
                "ok": False,
                "error": {"type": "not_found", "message": "tool not available"},
                "status_code": 404,
            }

        chat_calls: list[str] = []

        def fake_chat_completion(**kwargs):
            chat_calls.append("chat")
            return {"choices": [{"message": {"content": '{"routing":{"task":"Decide"}}'}}]}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="routing",
                prompt_text="Stage prompt",
                timeout_seconds=30,
                response_schema={
                    "type": "object",
                    "required": ["routing"],
                    "properties": {"routing": {"type": "object"}},
                },
            )

            self.assertEqual(tool_calls, ["tool:llm-task:json"])
            self.assertEqual(result.backend_name, "openclaw-chat")
            self.assertEqual(len(chat_calls), 1)
            self.assertEqual(
                read_runtime_config(config_path=config_path).executor_mode,
                "chat_fallback",
            )

    def test_openclaw_explicit_runtime_override_takes_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"
            write_runtime_config(config_path=config_path, executor_mode="chat_fallback")

            tool_calls: list[str] = []

            def fake_tool_invoke(*, tool, action, args):
                tool_calls.append(f"tool:{tool}:{action}")
                return {
                    "ok": True,
                    "result": {
                        "details": {
                            "json": {"routing": {"task": "Decide"}}
                        }
                    },
                }

            def fake_chat_completion(**kwargs):
                self.fail("explicit override should prevent chat fallback")

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                    runtime_mode="llm-task",
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="routing",
                prompt_text="Stage prompt",
                timeout_seconds=30,
                response_schema={
                    "type": "object",
                    "required": ["routing"],
                    "properties": {"routing": {"type": "object"}},
                },
            )

            self.assertEqual(tool_calls, ["tool:llm-task:json"])
            self.assertEqual(result.backend_name, "openclaw-llm-task")
            self.assertEqual(
                read_runtime_config(config_path=config_path).executor_mode,
                "chat_fallback",
            )

    def test_openclaw_downgrades_persisted_llm_task_to_chat_fallback(self) -> None:
        tool_calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            tool_calls.append(f"tool:{tool}:{action}")
            return {
                "ok": False,
                "error": {"type": "not_found", "message": "tool not available"},
                "status_code": 404,
            }

        chat_calls: list[str] = []

        def fake_chat_completion(**kwargs):
            chat_calls.append("chat")
            return {"choices": [{"message": {"content": '{"routing":{"task":"Decide"}}'}}]}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"
            write_runtime_config(config_path=config_path, executor_mode="llm-task")

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="routing",
                prompt_text="Stage prompt",
                timeout_seconds=30,
                response_schema={
                    "type": "object",
                    "required": ["routing"],
                    "properties": {"routing": {"type": "object"}},
                },
            )

            self.assertEqual(tool_calls, ["tool:llm-task:json"])
            self.assertEqual(chat_calls, ["chat"])
            self.assertEqual(result.backend_name, "openclaw-chat")
            self.assertEqual(
                read_runtime_config(config_path=config_path).executor_mode,
                "chat_fallback",
            )

    def test_stage_execution_result_carries_backend_trace_and_error_fields(self) -> None:
        result = StageExecutionResult(
            response_text='{"routing": {"task": "Decide"}}',
            backend_name="openclaw-chat",
            trace_text='{"id":"abc"}',
            error_text=None,
        )

        self.assertEqual(result.response_text, '{"routing": {"task": "Decide"}}')
        self.assertEqual(result.backend_name, "openclaw-chat")
        self.assertEqual(result.trace_text, '{"id":"abc"}')
        self.assertIsNone(result.error_text)

    def test_openclaw_json_executor_prefers_llm_task_when_available(self) -> None:
        calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            calls.append(f"tool:{tool}:{action}")
            return {
                "ok": True,
                "result": {
                    "details": {
                        "json": {"routing": {"task": "Decide"}}
                    }
                },
            }

        def fake_chat_completion(**kwargs):
            calls.append("chat")
            return {"choices": [{"message": {"content": '{"routing":{"task":"Decide"}}'}}]}

        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="routing",
                prompt_text="Stage prompt",
                timeout_seconds=30,
                response_schema={
                    "type": "object",
                    "required": ["routing"],
                    "properties": {"routing": {"type": "object"}},
                },
            )

        self.assertEqual(result.backend_name, "openclaw-llm-task")
        self.assertEqual(calls, ["tool:llm-task:json"])
        self.assertEqual(json.loads(result.response_text), {"routing": {"task": "Decide"}})

    def test_openclaw_json_executor_falls_back_to_chat_and_repairs_invalid_json_once(self) -> None:
        tool_calls: list[str] = []
        chat_prompts: list[str] = []
        chat_responses = iter(
            [
                {"choices": [{"message": {"content": "not json"}}]},
                {"choices": [{"message": {"content": '{"routing":{"task":"Decide"}}'}}]},
            ]
        )

        def fake_tool_invoke(*, tool, action, args):
            tool_calls.append(f"tool:{tool}:{action}")
            return {
                "ok": False,
                "error": {"type": "not_found", "message": "tool not available"},
                "status_code": 404,
            }

        def fake_chat_completion(**kwargs):
            chat_prompts.append(kwargs["prompt_text"])
            return next(chat_responses)

        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="routing",
                prompt_text="Stage prompt",
                timeout_seconds=30,
                response_schema={
                    "type": "object",
                    "required": ["routing"],
                    "properties": {"routing": {"type": "object"}},
                },
            )

        self.assertEqual(tool_calls, ["tool:llm-task:json"])
        self.assertEqual(result.backend_name, "openclaw-chat")
        self.assertEqual(json.loads(result.response_text), {"routing": {"task": "Decide"}})
        self.assertEqual(len(chat_prompts), 2)
        self.assertIn("return exactly one json object", chat_prompts[0].lower())
        self.assertIn("repair", chat_prompts[1].lower())

    def test_openclaw_json_executor_rejects_invalid_llm_task_payload_before_persisting_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                ),
                tool_invoker=lambda **kwargs: {
                    "ok": True,
                    "result": {"details": {"json": {"wrong_key": "oops"}}},
                },
                chat_completion_caller=lambda **kwargs: self.fail("chat fallback should not run for invalid llm-task payload"),
            )

            with self.assertRaises(ExecutorInvocationError) as raised:
                executor.run_stage_prompt(
                    stage="routing",
                    prompt_text="Stage prompt",
                    timeout_seconds=30,
                    response_schema={
                        "type": "object",
                        "required": ["routing"],
                        "properties": {"routing": {"type": "object"}},
                    },
                )

            self.assertEqual(raised.exception.backend_name, "openclaw-llm-task")
            self.assertEqual(read_runtime_config(config_path=config_path).executor_mode, "auto")

    def test_openclaw_json_executor_rejects_invalid_repair_output(self) -> None:
        chat_responses = iter(
            [
                {"choices": [{"message": {"content": "not json"}}]},
                {"choices": [{"message": {"content": '{"still":"wrong"}'}}]},
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                tool_invoker=lambda **kwargs: {
                    "ok": False,
                    "error": {"type": "not_found", "message": "tool not available"},
                    "status_code": 404,
                },
                chat_completion_caller=lambda **kwargs: next(chat_responses),
            )

            with self.assertRaises(ExecutorInvocationError) as raised:
                executor.run_stage_prompt(
                    stage="routing",
                    prompt_text="Stage prompt",
                    timeout_seconds=30,
                    response_schema={
                        "type": "object",
                        "required": ["routing"],
                        "properties": {"routing": {"type": "object"}},
                    },
                )

            self.assertEqual(raised.exception.backend_name, "openclaw-chat")
            self.assertEqual(raised.exception.failure_reason, "invalid_response")

    def test_openclaw_chat_executor_wraps_unexpected_response_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                chat_completion_caller=lambda **kwargs: {"choices": []},
            )

            with self.assertRaises(ExecutorInvocationError) as raised:
                executor.run_stage_prompt(
                    stage="render",
                    prompt_text="Render prompt",
                    timeout_seconds=30,
                    response_schema=None,
                )

            self.assertEqual(raised.exception.backend_name, "openclaw-chat")
            self.assertEqual(raised.exception.failure_reason, "invalid_response")

    def test_openclaw_chat_executor_retries_one_connection_reset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                    runtime_mode="chat_fallback",
                ),
            )

            responses = iter(
                [
                    self._FakeHttpResponse({"choices": [{"message": {"content": '{"routing":{"task":"Decide"}}'}}]}),
                ]
            )

            def flaky_urlopen(request, timeout=0):
                if not hasattr(flaky_urlopen, "called"):
                    flaky_urlopen.called = True
                    raise ConnectionResetError(104, "Connection reset by peer")
                return next(responses)

            with patch(
                "tools.question_generator.openclaw_executor.urllib.request.urlopen",
                side_effect=flaky_urlopen,
            ):
                result = executor.run_stage_prompt(
                    stage="routing",
                    prompt_text="Stage prompt",
                    timeout_seconds=30,
                    response_schema={
                        "type": "object",
                        "required": ["routing"],
                        "properties": {"routing": {"type": "object"}},
                    },
                )

            self.assertEqual(result.backend_name, "openclaw-chat")
            self.assertEqual(json.loads(result.response_text), {"routing": {"task": "Decide"}})

    def test_openclaw_chat_executor_wraps_repeated_connection_resets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                    runtime_mode="chat_fallback",
                ),
            )

            with patch(
                "tools.question_generator.openclaw_executor.urllib.request.urlopen",
                side_effect=ConnectionResetError(104, "Connection reset by peer"),
            ):
                with self.assertRaises(ExecutorInvocationError) as raised:
                    executor.run_stage_prompt(
                        stage="routing",
                        prompt_text="Stage prompt",
                        timeout_seconds=30,
                        response_schema={
                            "type": "object",
                            "required": ["routing"],
                            "properties": {"routing": {"type": "object"}},
                        },
                    )

            self.assertEqual(raised.exception.backend_name, "openclaw-chat")
            self.assertEqual(raised.exception.failure_reason, "transport_error")
            self.assertIn("Connection reset by peer", raised.exception.error_text)

    def test_render_stage_uses_plain_text_chat_path(self) -> None:
        tool_calls: list[str] = []
        chat_calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            tool_calls.append(f"tool:{tool}:{action}")
            return {
                "ok": True,
                "result": {},
            }

        def fake_chat_completion(**kwargs):
            chat_calls.append(kwargs["stage"])
            return {"choices": [{"message": {"content": "# Decision Memo\n\nProceed carefully."}}]}

        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                tool_invoker=fake_tool_invoke,
                chat_completion_caller=fake_chat_completion,
            )

            result = executor.run_stage_prompt(
                stage="render",
                prompt_text="Render prompt",
                timeout_seconds=30,
                response_schema=None,
            )

        self.assertEqual(result.backend_name, "openclaw-chat")
        self.assertEqual(tool_calls, [])
        self.assertEqual(chat_calls, ["render"])
        self.assertIn("# Decision Memo", result.response_text)


if __name__ == "__main__":
    unittest.main()
