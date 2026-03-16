import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests" / "question_generator"
REVIEW_SCHEMA_PATH = TESTS_DIR / "non_render_prompt_review_schema.json"


def make_review_payload(
    stage: str,
    *,
    hard_gates: dict | None = None,
    scores: dict | None = None,
    top_findings: list | None = None,
    overall_recommendation: str = "Accept",
    summary: str = "Clear and usable prompt.",
) -> dict:
    return {
        "stage": stage,
        "hard_gates": {
            "instruction_coherence": "PASS",
            "input_precedence_clarity": "PASS",
            "output_requirement_clarity": "PASS",
            "sufficient_starting_context": "PASS",
            **(hard_gates or {}),
        },
        "scores": {
            "task_clarity": 4,
            "context_usefulness": 4,
            "guidance_and_constraint_clarity": 4,
            "readability": 4,
            "output_readiness": 4,
            "confidence_to_execute": 4,
            "context_efficiency": 4,
            "risk_of_misinterpretation": 4,
            **(scores or {}),
        },
        "top_findings": top_findings or [],
        "overall_recommendation": overall_recommendation,
        "summary": summary,
    }


class NonRenderPromptQualityTest(unittest.TestCase):
    def test_review_schema_file_exists_and_has_expected_top_level_keys(self) -> None:
        with REVIEW_SCHEMA_PATH.open() as schema_file:
            schema = json.load(schema_file)

        self.assertEqual(schema["type"], "object")
        self.assertIn("stage", schema["properties"])
        self.assertIn("hard_gates", schema["properties"])
        self.assertIn("scores", schema["properties"])
        self.assertIn("top_findings", schema["properties"])
        self.assertIn("overall_recommendation", schema["properties"])
        self.assertIn("summary", schema["properties"])

    def test_review_prompt_and_workflow_doc_expect_json_array_of_stage_reviews(self) -> None:
        review_prompt = (TESTS_DIR / "non_render_prompt_review_prompt.md").read_text()
        workflow_doc = (TESTS_DIR / "non_render_prompt_quality.md").read_text()

        self.assertIn("Imagine you are the model who must do the work.", review_prompt)
        self.assertIn("Return one JSON array only.", review_prompt)
        self.assertIn("Instruction Coherence", review_prompt)
        self.assertIn("Sufficient Starting Context", review_prompt)
        self.assertIn("Confidence To Execute", review_prompt)
        self.assertIn("Risk Of Misinterpretation", review_prompt)
        self.assertIn("JSON array", workflow_doc)
        self.assertIn("local generated output", workflow_doc)
        self.assertIn("should remain untracked", workflow_doc)

    def test_non_render_stage_list_matches_expected_order(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import NON_RENDER_STAGES

        self.assertEqual(
            NON_RENDER_STAGES,
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
            ],
        )

    def test_choose_review_topic_is_seeded_and_repeatable(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import choose_review_topic

        self.assertEqual(
            choose_review_topic(seed=20260313),
            choose_review_topic(seed=20260313),
        )
        self.assertNotEqual(
            choose_review_topic(seed=20260313),
            choose_review_topic(seed=20260314),
        )

    def test_build_review_prompt_set_contains_all_non_render_stages_and_no_placeholders(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import (
            NON_RENDER_STAGES,
            build_review_prompt_set,
            choose_review_topic,
        )

        topic = choose_review_topic(seed=20260313)
        prompt_set = build_review_prompt_set(seed=20260313)

        self.assertEqual(prompt_set["topic"], topic)
        for stage in NON_RENDER_STAGES:
            prompt = prompt_set["prompts"][stage]
            self.assertTrue(prompt.splitlines()[0].strip())
            self.assertIn(topic, prompt)
            self.assertNotIn("{{topic}}", prompt)
            self.assertNotIn("{{current_state}}", prompt)
            self.assertNotIn("{{active_steering}}", prompt)
            self.assertNotIn("{{required_output}}", prompt)
            self.assertNotIn("{{feedback}}", prompt)
            self.assertNotIn('"$ref"', prompt)
            self.assertNotIn("## Relevant Context", prompt)
            self.assertNotIn("## Current State", prompt)
            self.assertNotIn("## Active Steering", prompt)
            self.assertEqual(
                prompt.count("[CONDITIONAL condition="),
                prompt.count("[/CONDITIONAL]"),
            )
            if stage == "routing":
                self.assertNotIn("## Stage Guidance", prompt)
            else:
                self.assertIn("## Stage Guidance", prompt)

    def test_review_prompt_set_expands_required_output_schema_for_llm_use(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import build_review_prompt_set

        prompt_set = build_review_prompt_set(seed=20260313)
        decision_logic_prompt = prompt_set["prompts"]["decision_logic"]

        self.assertIn("## Required Output", decision_logic_prompt)
        self.assertNotIn('"$ref"', decision_logic_prompt)
        self.assertIn('"must_know_before_action"', decision_logic_prompt)
        self.assertIn('"recommendation_or_action_frame"', decision_logic_prompt)

    def test_review_prompt_set_renders_repeated_scenarios_without_unresolved_mustache_tags(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import build_review_prompt_set

        prompt_set = build_review_prompt_set(seed=20260313)
        scenarios_prompt = prompt_set["prompts"]["scenarios"]

        self.assertNotIn("{{#", scenarios_prompt)
        self.assertNotIn("{{/", scenarios_prompt)
        self.assertNotIn("{{.", scenarios_prompt)
        self.assertIn("Structural model:", scenarios_prompt)

    def test_review_prompt_set_keeps_inline_context_human_readable(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import build_review_prompt_set

        prompt_set = build_review_prompt_set(seed=20260313)
        decision_logic_prompt = prompt_set["prompts"]["decision_logic"]
        before_guidance, remainder = decision_logic_prompt.split("## Stage Guidance", maxsplit=1)

        self.assertIn("Action frame:", before_guidance)
        self.assertIn("Evidence plan:", before_guidance)
        self.assertIn("[CONDITIONAL condition=", before_guidance)
        self.assertNotIn("## Relevant Context", before_guidance)
        self.assertIn("## Required Output", remainder)
        self.assertIn("```json", remainder)

    def test_prompt_set_cli_writes_manifest_and_stage_files(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import main

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "prompts"
            manifest_path = Path(tmpdir) / "manifest.json"
            exit_code = main(
                [
                    "--output-dir",
                    str(output_dir),
                    "--manifest",
                    str(manifest_path),
                    "--seed",
                    "20260313",
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(manifest_path.exists())
            self.assertTrue(output_dir.exists())
            manifest = json.loads(manifest_path.read_text())
            self.assertIn("topic", manifest)
            self.assertIn("prompts", manifest)
            self.assertEqual(len(manifest["prompts"]), 9)
            for item in manifest["prompts"]:
                self.assertTrue(Path(item["path"]).exists())

    def test_prompt_set_script_runs_directly_from_repo_root(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "prompts"
            manifest_path = Path(tmpdir) / "manifest.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "tests/question_generator/assemble_non_render_prompts.py",
                    "--output-dir",
                    str(output_dir),
                    "--manifest",
                    str(manifest_path),
                    "--seed",
                    "20260313",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(manifest_path.exists())
            self.assertTrue(output_dir.exists())

    def test_known_good_review_payload_validates_and_passes_hard_gates(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import (
            review_passes_hard_gates,
            validate_review_payload,
        )

        payload = make_review_payload(
            "decision_logic",
            scores={
                "task_clarity": 5,
                "context_usefulness": 4,
                "guidance_and_constraint_clarity": 5,
                "readability": 5,
                "output_readiness": 5,
                "confidence_to_execute": 4,
                "context_efficiency": 4,
                "risk_of_misinterpretation": 4,
            },
            overall_recommendation="Accept with minor improvements",
        )

        self.assertEqual(validate_review_payload(payload), [])
        self.assertTrue(review_passes_hard_gates(payload))

    def test_review_payload_with_failed_hard_gate_is_valid_but_fails_quality_gate(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import (
            review_passes_hard_gates,
            validate_review_payload,
        )

        payload = make_review_payload(
            "routing",
            hard_gates={"instruction_coherence": "FAIL"},
            scores={
                "task_clarity": 3,
                "context_usefulness": 3,
                "guidance_and_constraint_clarity": 3,
                "readability": 3,
                "output_readiness": 3,
                "confidence_to_execute": 3,
                "context_efficiency": 3,
                "risk_of_misinterpretation": 2,
            },
            top_findings=[
                {
                    "title": "Conflicting precedence rule",
                    "why_it_matters": "The analyst may not know which instruction should dominate.",
                    "prompt_evidence": "Two inputs are presented without precedence.",
                }
            ],
            overall_recommendation="Needs revision",
        )

        self.assertEqual(validate_review_payload(payload), [])
        self.assertFalse(review_passes_hard_gates(payload))

    def test_malformed_review_payload_returns_validation_errors(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import validate_review_payload

        payload = {
            "stage": "routing",
            "hard_gates": {
                "instruction_coherence": "PASS",
            },
            "scores": {
                "task_clarity": 6,
            },
            "top_findings": [],
            "overall_recommendation": "Accept",
            "summary": "Too incomplete to be valid.",
        }

        errors = validate_review_payload(payload)
        self.assertTrue(errors)
        self.assertTrue(any("hard_gates" in error or "scores" in error for error in errors))

    def test_validate_review_payload_rejects_extra_keys_and_boolean_scores(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import validate_review_payload

        payload = make_review_payload(
            "routing",
            hard_gates={"extra_gate": "PASS"},
            scores={"task_clarity": True, "extra_score": 4},
        )
        payload["extra_field"] = "not allowed"

        errors = validate_review_payload(payload)
        self.assertTrue(any("unexpected" in error for error in errors))
        self.assertTrue(any("task_clarity" in error for error in errors))

    def test_unknown_stage_is_rejected(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import validate_review_payload

        payload = make_review_payload("render")
        errors = validate_review_payload(payload)
        self.assertTrue(any("stage" in error for error in errors))

    def test_checker_cli_reports_scores_and_fails_on_hard_gate_failure(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import main

        payload = [
            make_review_payload("routing"),
            make_review_payload(
                "boundary",
                hard_gates={"instruction_coherence": "FAIL"},
                scores={
                    "task_clarity": 3,
                    "context_usefulness": 3,
                    "guidance_and_constraint_clarity": 3,
                    "readability": 3,
                    "output_readiness": 3,
                    "confidence_to_execute": 3,
                    "context_efficiency": 3,
                    "risk_of_misinterpretation": 2,
                },
                top_findings=[
                    {
                        "title": "Conflict",
                        "why_it_matters": "Could confuse the analyst.",
                        "prompt_evidence": "Two incompatible instructions are present.",
                    }
                ],
                overall_recommendation="Needs revision",
                summary="Fails one hard gate.",
            ),
            make_review_payload("structure"),
            make_review_payload("scenarios"),
            make_review_payload("question_generation"),
            make_review_payload("evidence_planning"),
            make_review_payload("decision_logic"),
            make_review_payload("signal_translation"),
            make_review_payload("monitoring"),
        ]

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--input", str(input_path)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Stage: routing", output)
        self.assertIn("Stage: boundary", output)
        self.assertIn("Scores: task=4", output)
        self.assertIn("Scores: task=3", output)
        self.assertIn("QUALITY REVIEW FAIL", output)

    def test_checker_cli_passes_when_all_hard_gates_pass(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import NON_RENDER_STAGES
        from tests.question_generator.check_non_render_prompt_review import main

        payload = [make_review_payload(stage, scores={"task_clarity": 5}) for stage in NON_RENDER_STAGES]

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--input", str(input_path)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("QUALITY REVIEW PASS", output)

    def test_checker_cli_fails_when_stage_set_is_incomplete(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import main

        payload = [make_review_payload("monitoring", scores={"task_clarity": 5})]

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--input", str(input_path)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("QUALITY REVIEW FAIL", output)

    def test_checker_cli_fails_cleanly_for_non_object_review_item(self) -> None:
        from tests.question_generator.check_non_render_prompt_review import main

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.json"
            input_path.write_text(json.dumps(["oops"]), encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["--input", str(input_path)])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("QUALITY REVIEW FAIL", output)

    def test_checker_script_runs_directly_from_repo_root(self) -> None:
        from tests.question_generator.assemble_non_render_prompts import NON_RENDER_STAGES

        payload = [make_review_payload(stage, scores={"task_clarity": 5}) for stage in NON_RENDER_STAGES]

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "review.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "tests/question_generator/check_non_render_prompt_review.py",
                    "--input",
                    str(input_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("QUALITY REVIEW PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
