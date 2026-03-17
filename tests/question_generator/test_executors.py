import json
import tempfile
from pathlib import Path
import unittest


from tools.question_generator.executors import ExecutorInvocationError, StageExecutionResult
from tools.question_generator.openclaw_config import (
    normalize_executor_mode,
    read_runtime_config,
    write_runtime_config,
)
from tools.question_generator.openclaw_executor import (
    OpenClawExecutorConfig,
    OpenClawStageExecutor,
)


class OpenClawExecutorTest(unittest.TestCase):
    def test_openclaw_runtime_config_defaults_to_session_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            runtime_config = read_runtime_config(config_path=config_path)

            self.assertEqual(runtime_config.executor_mode, "session")

    def test_openclaw_executor_bootstraps_missing_runtime_config_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                ),
                gateway_caller=lambda **kwargs: self.fail("gateway should not be called during config bootstrap"),
            )

            self.assertTrue(config_path.is_file())
            self.assertEqual(
                json.loads(config_path.read_text(encoding="utf-8")),
                {"json_executor": "session"},
            )

    def test_openclaw_runtime_config_normalizes_legacy_modes_to_session(self) -> None:
        self.assertEqual(normalize_executor_mode(None), "session")
        self.assertEqual(normalize_executor_mode("auto"), "session")
        self.assertEqual(normalize_executor_mode("chat_fallback"), "session")
        self.assertEqual(normalize_executor_mode("chat-fallback"), "session")

    def test_openclaw_llm_task_mode_persists_llm_task_after_success(self) -> None:
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
                    runtime_mode="llm-task",
                ),
                tool_invoker=fake_tool_invoke,
                gateway_caller=fake_chat_completion,
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
                "session",
            )

    def test_openclaw_session_mode_is_used_by_default(self) -> None:
        gateway_calls: list[str] = []

        history_responses = iter(
            [
                {"messages": [{"role": "assistant", "content": '{"routing":{"task":"Decide"}}'}]},
            ]
        )

        def fake_gateway_call(*, method, params, timeout_seconds):
            gateway_calls.append(method)
            if method == "chat.send":
                return {"ok": True, "runId": "run-1"}
            if method == "chat.history":
                return next(history_responses)
            self.fail(f"unexpected method: {method}")

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                ),
                gateway_caller=fake_gateway_call,
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

            self.assertEqual(result.backend_name, "openclaw-session")
            self.assertEqual(gateway_calls, ["chat.send", "chat.history"])
            self.assertEqual(
                read_runtime_config(config_path=config_path).executor_mode,
                "session",
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

            def fake_gateway_call(**kwargs):
                self.fail("explicit llm-task should prevent session fallback")

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                    runtime_mode="llm-task",
                ),
                tool_invoker=fake_tool_invoke,
                gateway_caller=fake_gateway_call,
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
                "session",
            )

    def test_openclaw_downgrades_persisted_llm_task_to_session_when_unavailable(self) -> None:
        tool_calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            tool_calls.append(f"tool:{tool}:{action}")
            return {
                "ok": False,
                "error": {"type": "not_found", "message": "tool not available"},
                "status_code": 404,
            }

        gateway_calls: list[str] = []

        history_responses = iter(
            [
                {"messages": [{"role": "user", "content": "Stage prompt"}]},
                {
                    "messages": [
                        {"role": "user", "content": "Stage prompt"},
                        {"role": "assistant", "content": '{"routing":{"task":"Decide"}}'},
                    ]
                },
            ]
        )

        def fake_gateway_call(*, method, params, timeout_seconds):
            gateway_calls.append(method)
            if method == "chat.send":
                return {"ok": True, "runId": "run-1"}
            if method == "chat.history":
                return next(history_responses)
            self.fail(f"unexpected method: {method}")

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
                gateway_caller=fake_gateway_call,
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
            self.assertEqual(gateway_calls, ["chat.send", "chat.history", "chat.history"])
            self.assertEqual(result.backend_name, "openclaw-session")
            self.assertEqual(
                read_runtime_config(config_path=config_path).executor_mode,
                "session",
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

    def test_openclaw_session_executor_repairs_invalid_json_once(self) -> None:
        gateway_calls: list[tuple[str, str]] = []
        history_responses = iter(
            [
                {"messages": [{"role": "assistant", "content": "not json"}]},
                {
                    "messages": [
                        {"role": "assistant", "content": "not json"},
                        {"role": "assistant", "content": '{"routing":{"task":"Decide"}}'},
                    ]
                },
            ]
        )

        def fake_gateway_call(*, method, params, timeout_seconds):
            gateway_calls.append((method, json.dumps(params, ensure_ascii=True)))
            if method == "chat.send":
                return {"ok": True, "runId": f"run-{len(gateway_calls)}"}
            if method == "chat.history":
                return next(history_responses)
            self.fail(f"unexpected method: {method}")

        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                gateway_caller=fake_gateway_call,
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

        self.assertEqual(result.backend_name, "openclaw-session")
        self.assertEqual(json.loads(result.response_text), {"routing": {"task": "Decide"}})
        send_payloads = [payload for method, payload in gateway_calls if method == "chat.send"]
        self.assertEqual(len(send_payloads), 2)
        self.assertIn("return exactly one json object", send_payloads[0].lower())
        self.assertIn("repair", send_payloads[1].lower())

    def test_openclaw_json_executor_rejects_invalid_llm_task_payload_before_persisting_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "runtime.json"

            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=config_path,
                    runtime_mode="llm-task",
                ),
                tool_invoker=lambda **kwargs: {
                    "ok": True,
                    "result": {"details": {"json": {"wrong_key": "oops"}}},
                },
                gateway_caller=lambda **kwargs: self.fail("session fallback should not run for invalid llm-task payload"),
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
            self.assertEqual(read_runtime_config(config_path=config_path).executor_mode, "session")

    def test_openclaw_session_executor_rejects_invalid_repair_output(self) -> None:
        history_responses = iter(
            [
                {"messages": [{"role": "assistant", "content": "not json"}]},
                {"messages": [{"role": "assistant", "content": '{"still":"wrong"}'}]},
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
                gateway_caller=lambda **kwargs: (
                    {"ok": True, "runId": "run-1"}
                    if kwargs["method"] == "chat.send"
                    else next(history_responses)
                ),
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

            self.assertEqual(raised.exception.backend_name, "openclaw-session")
            self.assertEqual(raised.exception.failure_reason, "invalid_response")

    def test_openclaw_session_executor_wraps_unexpected_response_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                gateway_caller=lambda **kwargs: (
                    {"ok": True, "runId": "run-1"}
                    if kwargs["method"] == "chat.send"
                    else {"messages": []}
                ),
            )

            with self.assertRaises(ExecutorInvocationError) as raised:
                executor.run_stage_prompt(
                    stage="render",
                    prompt_text="Render prompt",
                    timeout_seconds=1,
                    response_schema=None,
                )

            self.assertEqual(raised.exception.backend_name, "openclaw-session")
            self.assertEqual(raised.exception.failure_reason, "timeout")

    def test_render_stage_uses_plain_text_chat_path(self) -> None:
        tool_calls: list[str] = []
        gateway_calls: list[str] = []

        def fake_tool_invoke(*, tool, action, args):
            tool_calls.append(f"tool:{tool}:{action}")
            return {
                "ok": True,
                "result": {},
            }

        def fake_gateway_call(*, method, params, timeout_seconds):
            gateway_calls.append(method)
            if method == "chat.send":
                return {"ok": True, "runId": "run-1"}
            if method == "chat.history":
                return {"messages": [{"role": "assistant", "content": "# Decision Memo\n\nProceed carefully."}]}
            self.fail(f"unexpected method: {method}")

        with tempfile.TemporaryDirectory() as temp_dir:
            executor = OpenClawStageExecutor(
                config=OpenClawExecutorConfig(
                    base_url="http://127.0.0.1:18789",
                    token="secret",
                    agent_id="main",
                    runtime_config_path=Path(temp_dir) / "runtime.json",
                ),
                tool_invoker=fake_tool_invoke,
                gateway_caller=fake_gateway_call,
            )

            result = executor.run_stage_prompt(
                stage="render",
                prompt_text="Render prompt",
                timeout_seconds=30,
                response_schema=None,
            )

        self.assertEqual(result.backend_name, "openclaw-session")
        self.assertEqual(tool_calls, [])
        self.assertEqual(gateway_calls, ["chat.send", "chat.history"])
        self.assertIn("# Decision Memo", result.response_text)


if __name__ == "__main__":
    unittest.main()
