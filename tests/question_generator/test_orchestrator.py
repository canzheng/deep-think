import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


from tools.question_generator.orchestrator import (
    ANSWERING_MODEL,
    ANSWERING_REASONING_EFFORT,
    DEFAULT_TIMEOUT_SECONDS,
    MANIFEST_FILENAME,
    RESPONSE_SCHEMA_FILENAME,
    SHARED_STATE_FILENAME,
    apply_stage_response,
    build_codex_exec_command,
    build_stage_agent_prompt,
    build_stage_response_schema,
    initialize_run,
    load_recipe,
    load_run_manifest,
    prepare_stage,
    run_recipe,
    run_stage,
)


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parents[2]
MINIMAL_STATE_PATH = FIXTURES_DIR / "minimal_state.json"
RECIPE_PATH = (
    REPO_ROOT
    / "prompt"
    / "question-generator"
    / "recipes"
    / "non-render.recipe.json"
)


class OrchestratorTest(unittest.TestCase):
    def test_default_timeout_is_120_seconds(self) -> None:
        self.assertEqual(DEFAULT_TIMEOUT_SECONDS, 120)

    def test_load_recipe_reads_non_render_stage_sequence(self) -> None:
        recipe = load_recipe(RECIPE_PATH)

        self.assertEqual(recipe["name"], "question_generator_workflow")
        self.assertEqual(recipe["stages"][0]["stage"], "routing")
        self.assertEqual(recipe["stages"][-1]["stage"], "render")
        self.assertEqual(len(recipe["stages"]), 10)

    def test_initialize_run_creates_manifest_and_shared_state_copy(self) -> None:
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )

            self.assertEqual(run_dir, Path(tmpdir) / "demo-run")
            self.assertTrue((run_dir / SHARED_STATE_FILENAME).is_file())
            self.assertTrue((run_dir / MANIFEST_FILENAME).is_file())

            manifest = load_run_manifest(run_dir)
            self.assertEqual(manifest["run_id"], "demo-run")
            self.assertEqual(manifest["state_path"], str(run_dir / SHARED_STATE_FILENAME))
            self.assertEqual(manifest["stages"], {})

    def test_prepare_stage_writes_prompt_artifact(self) -> None:
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )

            result = prepare_stage(run_dir, "decision_logic")

            prompt_path = Path(result["prompt_path"])
            self.assertTrue(prompt_path.is_file())
            self.assertIn("You are converting the current analysis into decision logic.", prompt_path.read_text(encoding="utf-8"))

            manifest = load_run_manifest(run_dir)
            stage_record = manifest["stages"]["decision_logic"]
            self.assertEqual(stage_record["status"], "prompt_prepared")
            self.assertEqual(stage_record["prompt_path"], str(prompt_path))
            self.assertEqual(stage_record["stage"], "decision_logic")
            self.assertTrue((prompt_path.parent / RESPONSE_SCHEMA_FILENAME).is_file())

    def test_prepare_stage_for_render_skips_response_schema_artifact(self) -> None:
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )

            result = prepare_stage(run_dir, "render")

            prompt_path = Path(result["prompt_path"])
            self.assertTrue(prompt_path.is_file())
            self.assertFalse((prompt_path.parent / RESPONSE_SCHEMA_FILENAME).exists())

            manifest = load_run_manifest(run_dir)
            stage_record = manifest["stages"]["render"]
            self.assertEqual(stage_record["status"], "prompt_prepared")
            self.assertNotIn("response_schema_path", stage_record)

    def test_build_stage_response_schema_adds_optional_feedback_when_supported(self) -> None:
        schema = build_stage_response_schema("question_generation")

        self.assertEqual(schema["type"], "object")
        self.assertIn("questions", schema["properties"])
        self.assertIn("feedback", schema["properties"])
        self.assertEqual(schema["properties"]["feedback"]["type"], ["object", "null"])

    def test_build_stage_response_schema_makes_optional_routing_fields_nullable_and_required(self) -> None:
        schema = build_stage_response_schema("routing")
        routing_schema = schema["properties"]["routing"]
        classification_rationales = routing_schema["properties"]["classification_rationales"]

        self.assertIn("secondary_task", routing_schema["required"])
        self.assertIn("secondary_domain", routing_schema["required"])
        self.assertEqual(
            routing_schema["properties"]["secondary_task"]["type"],
            ["string", "null"],
        )
        self.assertIn("secondary_task", classification_rationales["required"])
        self.assertEqual(
            classification_rationales["properties"]["secondary_task"]["type"],
            ["string", "null"],
        )

    def test_build_codex_exec_command_pins_model_reasoning_and_ephemeral_session(self) -> None:
        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            command = build_codex_exec_command(
                stage="decision_logic",
                codex_bin="codex",
                workspace_dir=REPO_ROOT,
                response_schema_path=artifact_dir / RESPONSE_SCHEMA_FILENAME,
                response_raw_path=artifact_dir / "response.raw.md",
            )

        self.assertEqual(command[0:2], ["codex", "exec"])
        self.assertIn("--ephemeral", command)
        self.assertIn("--json", command)
        self.assertIn("-m", command)
        self.assertIn(ANSWERING_MODEL, command)
        self.assertIn("-c", command)
        self.assertIn(f'reasoning_effort="{ANSWERING_REASONING_EFFORT}"', command)
        self.assertIn("--output-schema", command)
        self.assertIn("-", command)

    def test_build_codex_exec_command_omits_output_schema_for_render(self) -> None:
        with TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir)
            command = build_codex_exec_command(
                stage="render",
                codex_bin="codex",
                workspace_dir=REPO_ROOT,
                response_schema_path=artifact_dir / RESPONSE_SCHEMA_FILENAME,
                response_raw_path=artifact_dir / "response.raw.md",
            )

        self.assertEqual(command[0:2], ["codex", "exec"])
        self.assertNotIn("--output-schema", command)
        self.assertNotIn("--json", command)
        self.assertIn("-o", command)
        self.assertEqual(command[-1], "-")

    def test_build_stage_agent_prompt_forbids_tools_and_requires_json_only(self) -> None:
        prompt = build_stage_agent_prompt("decision_logic", "Stage body")

        self.assertIn("Do not run shell commands", prompt)
        self.assertIn("Do not inspect files", prompt)
        self.assertIn("Return exactly one JSON object", prompt)
        self.assertIn("Stage body", prompt)

    def test_build_stage_agent_prompt_for_render_asks_for_direct_deliverable(self) -> None:
        prompt = build_stage_agent_prompt("render", "Stage body")

        self.assertIn("Do not run shell commands", prompt)
        self.assertIn("Return the final deliverable directly as plain text.", prompt)
        self.assertNotIn("Return exactly one JSON object", prompt)
        self.assertNotIn("Do not include markdown fences or explanatory prose.", prompt)
        self.assertIn("Stage body", prompt)

    def test_apply_stage_response_persists_raw_and_parsed_payload_and_merges_owned_sections(self) -> None:
        response_text = """Here is the stage result:

```json
{
  "decision_logic": {
    "must_know_before_action": ["confirm valuation discipline"],
    "can_learn_after_action": ["short-term estimate drift"]
  },
  "synthesis": {
    "recommendation_or_action_frame": "wait for confirmation"
  }
}
```
"""
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )
            prepare_stage(run_dir, "decision_logic")

            result = apply_stage_response(
                run_dir,
                "decision_logic",
                response_text=response_text,
            )

            raw_path = Path(result["response_raw_path"])
            parsed_path = Path(result["response_parsed_path"])
            self.assertTrue(raw_path.is_file())
            self.assertTrue(parsed_path.is_file())
            self.assertIn("Here is the stage result:", raw_path.read_text(encoding="utf-8"))

            with parsed_path.open() as parsed_file:
                parsed = json.load(parsed_file)
            self.assertEqual(
                parsed["decision_logic"]["must_know_before_action"],
                ["confirm valuation discipline"],
            )

            with (run_dir / SHARED_STATE_FILENAME).open() as state_file:
                state = json.load(state_file)
            self.assertEqual(
                state["decision_logic"]["must_know_before_action"],
                ["confirm valuation discipline"],
            )
            self.assertEqual(
                state["synthesis"]["recommendation_or_action_frame"],
                "wait for confirmation",
            )

            manifest = load_run_manifest(run_dir)
            stage_record = manifest["stages"]["decision_logic"]
            self.assertEqual(stage_record["status"], "response_applied")
            self.assertEqual(stage_record["response_raw_path"], str(raw_path))
            self.assertEqual(stage_record["response_parsed_path"], str(parsed_path))

    def test_apply_stage_response_rejects_unowned_top_level_sections(self) -> None:
        bad_response = """```json
{
  "decision_logic": {
    "must_know_before_action": ["confirm valuation discipline"]
  },
  "routing": {
    "task": "Decide"
  }
}
```"""
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )
            prepare_stage(run_dir, "decision_logic")

            with self.assertRaises(ValueError):
                apply_stage_response(
                    run_dir,
                    "decision_logic",
                    response_text=bad_response,
                )

    def test_apply_stage_response_for_render_persists_text_without_json_parsing(self) -> None:
        response_text = "# Investment Worksheet\n\nDecision: wait for confirmation."

        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )
            prepare_stage(run_dir, "render")

            result = apply_stage_response(
                run_dir,
                "render",
                response_text=response_text,
            )

            raw_path = Path(result["response_raw_path"])
            self.assertTrue(raw_path.is_file())
            self.assertEqual(raw_path.read_text(encoding="utf-8"), response_text)
            self.assertNotIn("response_parsed_path", result)

            manifest = load_run_manifest(run_dir)
            stage_record = manifest["stages"]["render"]
            self.assertEqual(stage_record["status"], "response_applied")
            self.assertEqual(stage_record["response_raw_path"], str(raw_path))
            self.assertNotIn("response_parsed_path", stage_record)

            with (run_dir / SHARED_STATE_FILENAME).open() as state_file:
                state = json.load(state_file)
            self.assertNotIn("deliverable", state)

    def test_run_stage_invokes_codex_and_applies_response(self) -> None:
        response_text = """{
  "decision_logic": {
    "must_know_before_action": ["confirm valuation discipline"]
  },
  "synthesis": {
    "recommendation_or_action_frame": "wait for confirmation"
  }
}"""

        def fake_run(command, *, input, text, capture_output, timeout, check):
            raw_path = Path(command[command.index("-o") + 1])
            raw_path.write_text(response_text, encoding="utf-8")
            self.assertIn("Do not run shell commands", input)
            self.assertIn("Return exactly one JSON object", input)
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout='{"event":"done"}\n',
                stderr="",
            )

        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )

            with patch("tools.question_generator.orchestrator.subprocess.run", side_effect=fake_run) as mocked_run:
                result = run_stage(run_dir, "decision_logic", codex_bin="codex", timeout_seconds=30)

            self.assertTrue(mocked_run.called)
            self.assertEqual(result["status"], "response_applied")
            self.assertEqual(result["model"], ANSWERING_MODEL)
            self.assertEqual(result["reasoning_effort"], ANSWERING_REASONING_EFFORT)
            self.assertTrue(result["ephemeral"])
            self.assertTrue(Path(result["codex_stdout_path"]).is_file())
            self.assertTrue(Path(result["codex_stderr_path"]).is_file())
            self.assertTrue(Path(result["response_raw_path"]).is_file())
            self.assertTrue(Path(result["response_parsed_path"]).is_file())

            with (run_dir / SHARED_STATE_FILENAME).open() as state_file:
                state = json.load(state_file)
            self.assertEqual(
                state["synthesis"]["recommendation_or_action_frame"],
                "wait for confirmation",
            )

    def test_run_stage_records_failure_without_merging_state(self) -> None:
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )

            with patch(
                "tools.question_generator.orchestrator.subprocess.run",
                return_value=subprocess.CompletedProcess(
                    args=["codex", "exec"],
                    returncode=1,
                    stdout="",
                    stderr="boom",
                ),
            ):
                with self.assertRaises(RuntimeError):
                    run_stage(run_dir, "decision_logic", codex_bin="codex", timeout_seconds=30)

            manifest = load_run_manifest(run_dir)
            stage_record = manifest["stages"]["decision_logic"]
            self.assertEqual(stage_record["status"], "codex_failed")
            self.assertEqual(stage_record["model"], ANSWERING_MODEL)
            self.assertTrue(Path(stage_record["codex_stderr_path"]).is_file())

    def test_run_stage_records_timeout_when_timeout_expired_returns_bytes(self) -> None:
        with TemporaryDirectory() as tmpdir:
            run_dir = initialize_run(
                state_path=MINIMAL_STATE_PATH,
                output_dir=Path(tmpdir),
                run_id="demo-run",
            )

            timeout_error = subprocess.TimeoutExpired(
                cmd=["codex", "exec"],
                timeout=30,
                output=b'{"event":"waiting"}\n',
                stderr=b"still running",
            )

            with patch(
                "tools.question_generator.orchestrator.subprocess.run",
                side_effect=timeout_error,
            ):
                with self.assertRaises(RuntimeError):
                    run_stage(run_dir, "decision_logic", codex_bin="codex", timeout_seconds=30)

            manifest = load_run_manifest(run_dir)
            stage_record = manifest["stages"]["decision_logic"]
            self.assertEqual(stage_record["status"], "codex_failed")
            self.assertEqual(stage_record["failure_reason"], "timeout")
            stdout_path = Path(stage_record["codex_stdout_path"])
            stderr_path = Path(stage_record["codex_stderr_path"])
            self.assertTrue(stdout_path.is_file())
            self.assertTrue(stderr_path.is_file())
            self.assertIn('"event":"waiting"', stdout_path.read_text(encoding="utf-8"))
            self.assertIn("still running", stderr_path.read_text(encoding="utf-8"))

    def test_run_recipe_initializes_run_and_executes_stages_in_recipe_order(self) -> None:
        executed_stages: list[str] = []

        def fake_run_stage(run_dir, stage, **kwargs):
            executed_stages.append(stage)
            return {
                "stage": stage,
                "status": "response_applied",
                "response_parsed_path": str(Path(run_dir) / "stages" / stage / "response.parsed.json"),
            }

        with TemporaryDirectory() as tmpdir:
            with patch("tools.question_generator.orchestrator.run_stage", side_effect=fake_run_stage):
                result = run_recipe(
                    recipe_path=RECIPE_PATH,
                    state_path=MINIMAL_STATE_PATH,
                    output_dir=Path(tmpdir),
                    run_id="demo-run",
                )

            self.assertEqual(result["run_dir"], str(Path(tmpdir) / "demo-run"))
            self.assertEqual(
                executed_stages,
                [
                    "routing",
                    "boundary",
                    "structure",
                    "scenarios",
                    "question_generation",
                    "evidence_planning",
                    "decision_logic",
                    "signal_translation",
                    "monitoring",
                    "render",
                ],
            )
            self.assertEqual(len(result["stages"]), 10)


if __name__ == "__main__":
    unittest.main()
