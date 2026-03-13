import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


from tools.question_generator.cli import build_workflow_parser, main


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "minimal_state.json"
)
RECIPE_PATH = (
    Path(__file__).resolve().parents[2]
    / "prompt"
    / "question-generator"
    / "recipes"
    / "non-render.recipe.json"
)


class CliTest(unittest.TestCase):
    def test_run_commands_default_timeout_to_120_seconds(self) -> None:
        parser = build_workflow_parser()

        run_stage_args = parser.parse_args(
            [
                "run-stage",
                "--run-dir",
                "/tmp/demo-run",
                "--stage",
                "decision_logic",
            ]
        )
        run_recipe_args = parser.parse_args(
            [
                "run-recipe",
                "--recipe",
                str(RECIPE_PATH),
                "--state",
                str(FIXTURE_PATH),
                "--output-dir",
                "/tmp/question-runs",
                "--run-id",
                "demo-run",
            ]
        )

        self.assertEqual(run_stage_args.timeout_seconds, 120)
        self.assertEqual(run_recipe_args.timeout_seconds, 120)

    def test_cli_prints_assembled_prompt(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "--stage",
                    "decision_logic",
                    "--state",
                    str(FIXTURE_PATH),
                    "--include-optional",
                    "structure",
                    "--include-optional",
                    "question_generation",
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("You are converting the current analysis into decision logic.", output)
        self.assertIn("## Relevant Context", output)
        self.assertIn("## Stage Guidance", output)
        self.assertIn("## Required Output", output)

    def test_init_run_prepare_stage_and_apply_response_commands(self) -> None:
        with TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "init-run",
                        "--state",
                        str(FIXTURE_PATH),
                        "--output-dir",
                        tmpdir,
                        "--run-id",
                        "demo-run",
                    ]
                )

            self.assertEqual(exit_code, 0)
            run_dir = Path(tmpdir) / "demo-run"
            self.assertTrue(run_dir.is_dir())
            self.assertIn(str(run_dir), stdout.getvalue())

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "prepare-stage",
                        "--run-dir",
                        str(run_dir),
                        "--stage",
                        "decision_logic",
                    ]
                )

            self.assertEqual(exit_code, 0)
            prompt_path = run_dir / "stages" / "07-decision-logic" / "prompt.md"
            self.assertTrue(prompt_path.is_file())
            self.assertIn(str(prompt_path), stdout.getvalue())

            response_path = run_dir / "decision_logic.response.md"
            response_path.write_text(
                """```json
{
  "decision_logic": {
    "must_know_before_action": ["confirm valuation discipline"]
  },
  "synthesis": {
    "recommendation_or_action_frame": "wait for confirmation"
  }
}
```""",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "apply-response",
                        "--run-dir",
                        str(run_dir),
                        "--stage",
                        "decision_logic",
                        "--response",
                        str(response_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("response.parsed.json", stdout.getvalue())
            self.assertTrue(
                (run_dir / "stages" / "07-decision-logic" / "response.parsed.json").is_file()
            )

    def test_run_stage_command_uses_orchestrator_execution_path(self) -> None:
        with TemporaryDirectory() as tmpdir:
            run_dir = Path(tmpdir) / "demo-run"
            run_dir.mkdir(parents=True, exist_ok=True)

            with patch(
                "tools.question_generator.cli.run_stage",
                return_value={
                    "response_parsed_path": str(run_dir / "stages" / "07-decision-logic" / "response.parsed.json")
                },
            ) as mocked_run_stage:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "run-stage",
                            "--run-dir",
                            str(run_dir),
                            "--stage",
                            "decision_logic",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_run_stage.called)
            self.assertIn("response.parsed.json", stdout.getvalue())

    def test_run_recipe_command_uses_recipe_runner_and_output_dir(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with patch(
                "tools.question_generator.cli.run_recipe",
                return_value={
                    "run_dir": str(Path(tmpdir) / "demo-run"),
                    "stages": [{"stage": "routing"}, {"stage": "monitoring"}],
                },
            ) as mocked_run_recipe:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "run-recipe",
                            "--recipe",
                            str(RECIPE_PATH),
                            "--state",
                            str(FIXTURE_PATH),
                            "--output-dir",
                            tmpdir,
                            "--run-id",
                            "demo-run",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_run_recipe.called)
            self.assertIn("demo-run", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
