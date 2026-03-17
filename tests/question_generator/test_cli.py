import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


from tools.question_generator.cli import build_workflow_parser, main
from tools.question_generator.codex_package import default_codex_package_dir
from tools.question_generator.openclaw_package import default_openclaw_package_dir


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
    def test_run_commands_default_timeout_to_500_seconds(self) -> None:
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

        self.assertEqual(run_stage_args.timeout_seconds, 500)
        self.assertEqual(run_recipe_args.timeout_seconds, 500)

    def test_new_workflow_commands_parse_expected_arguments(self) -> None:
        parser = build_workflow_parser()

        init_args = parser.parse_args(
            [
                "init-run",
                "--state",
                str(FIXTURE_PATH),
                "--output-dir",
                "/tmp/question-runs",
                "--run-id",
                "demo-run",
                "--output-language",
                "French",
            ]
        )
        init_topic_args = parser.parse_args(
            [
                "init-topic-run",
                "--topic",
                "Should Atlas expand into healthcare?",
                "--output-dir",
                "/tmp/question-runs",
                "--run-id",
                "topic-run",
                "--output-language",
                "Japanese",
            ]
        )
        update_routing_args = parser.parse_args(
            [
                "update-routing",
                "--run-dir",
                "/tmp/question-runs/topic-run",
                "--patch-json",
                '{"output_mode":"Research Memo"}',
            ]
        )
        run_on_run_args = parser.parse_args(
            [
                "run-recipe-on-run",
                "--recipe",
                str(RECIPE_PATH),
                "--run-dir",
                "/tmp/question-runs/topic-run",
                "--start-stage",
                "boundary",
            ]
        )
        run_topic_args = parser.parse_args(
            [
                "run-topic",
                "--topic",
                "Should Atlas expand into healthcare?",
                "--recipe",
                str(RECIPE_PATH),
                "--output-dir",
                "/tmp/question-runs",
                "--run-id",
                "topic-run",
                "--pause-after-stage",
                "routing",
                "--executor-backend",
                "openclaw",
                "--output-language",
                "Simplified Chinese",
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
                "--output-language",
                "Spanish",
            ]
        )
        refresh_package_args = parser.parse_args(
            [
                "refresh-openclaw-package",
            ]
        )
        refresh_codex_package_args = parser.parse_args(
            [
                "refresh-codex-package",
            ]
        )

        self.assertEqual(init_args.output_language, "French")
        self.assertEqual(init_topic_args.run_id, "topic-run")
        self.assertEqual(init_topic_args.output_language, "Japanese")
        self.assertEqual(update_routing_args.patch_json, '{"output_mode":"Research Memo"}')
        self.assertEqual(run_on_run_args.start_stage, "boundary")
        self.assertEqual(run_recipe_args.output_language, "Spanish")
        self.assertEqual(run_topic_args.pause_after_stage, "routing")
        self.assertEqual(run_topic_args.executor_backend, "openclaw")
        self.assertEqual(run_topic_args.output_language, "Simplified Chinese")
        self.assertEqual(Path(refresh_package_args.output_dir), default_openclaw_package_dir())
        self.assertEqual(Path(refresh_codex_package_args.output_dir), default_codex_package_dir())

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
        self.assertNotIn("## Relevant Context", output)
        self.assertNotIn("## Current State", output)
        self.assertIn("## Stage Guidance", output)
        self.assertNotIn("## Active Steering", output)
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
                            "--executor-backend",
                            "openclaw",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_run_stage.called)
            self.assertEqual(mocked_run_stage.call_args.kwargs["executor_backend"], "openclaw")
            self.assertIn("response.parsed.json", stdout.getvalue())

    def test_run_recipe_command_uses_recipe_runner_and_output_dir(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with patch(
                "tools.question_generator.cli.run_recipe",
                return_value={
                    "run_dir": str(Path(tmpdir) / "demo-run"),
                    "stages": [{"stage": "routing"}, {"stage": "render"}],
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
                            "--executor-backend",
                            "openclaw",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_run_recipe.called)
            self.assertEqual(mocked_run_recipe.call_args.kwargs["executor_backend"], "openclaw")
            self.assertIn("demo-run", stdout.getvalue())

    def test_init_topic_run_command_uses_topic_initializer(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with patch(
                "tools.question_generator.cli.initialize_topic_run",
                return_value=Path(tmpdir) / "topic-run",
            ) as mocked_initialize_topic_run:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "init-topic-run",
                            "--topic",
                            "Should Atlas expand into healthcare?",
                            "--output-dir",
                            tmpdir,
                            "--run-id",
                            "topic-run",
                            "--output-language",
                            "Italian",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_initialize_topic_run.called)
            self.assertEqual(mocked_initialize_topic_run.call_args.kwargs["output_language"], "Italian")
            self.assertIn("topic-run", stdout.getvalue())

    def test_update_routing_command_uses_routing_patcher(self) -> None:
        with patch(
            "tools.question_generator.cli.update_routing",
            return_value={"output_mode": "Research Memo"},
        ) as mocked_update_routing:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "update-routing",
                        "--run-dir",
                        "/tmp/question-runs/topic-run",
                        "--patch-json",
                        '{"output_mode":"Research Memo"}',
                    ]
                )

        self.assertEqual(exit_code, 0)
        self.assertTrue(mocked_update_routing.called)
        self.assertIn("Research Memo", stdout.getvalue())

    def test_run_recipe_on_run_command_uses_existing_run_recipe_runner(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with patch(
                "tools.question_generator.cli.run_recipe_on_run",
                return_value={
                    "run_dir": str(Path(tmpdir) / "topic-run"),
                    "stages": [{"stage": "boundary"}, {"stage": "render"}],
                },
            ) as mocked_run_recipe_on_run:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "run-recipe-on-run",
                            "--recipe",
                            str(RECIPE_PATH),
                            "--run-dir",
                            str(Path(tmpdir) / "topic-run"),
                            "--start-stage",
                            "boundary",
                            "--executor-backend",
                            "openclaw",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_run_recipe_on_run.called)
            self.assertEqual(mocked_run_recipe_on_run.call_args.kwargs["executor_backend"], "openclaw")
            self.assertIn("topic-run", stdout.getvalue())

    def test_run_topic_command_uses_topic_runner(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with patch(
                "tools.question_generator.cli.run_topic",
                return_value={
                    "run_dir": str(Path(tmpdir) / "topic-run"),
                    "stages": [{"stage": "routing"}],
                },
            ) as mocked_run_topic:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "run-topic",
                            "--topic",
                            "Should Atlas expand into healthcare?",
                            "--recipe",
                            str(RECIPE_PATH),
                            "--output-dir",
                            tmpdir,
                            "--run-id",
                            "topic-run",
                            "--pause-after-stage",
                            "routing",
                            "--executor-backend",
                            "openclaw",
                            "--output-language",
                            "German",
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_run_topic.called)
            self.assertEqual(mocked_run_topic.call_args.kwargs["executor_backend"], "openclaw")
            self.assertEqual(mocked_run_topic.call_args.kwargs["output_language"], "German")
            self.assertIn("topic-run", stdout.getvalue())

    def test_refresh_openclaw_package_command_uses_package_builder(self) -> None:
        with TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "openclaw-package"
            with patch(
                "tools.question_generator.cli.refresh_openclaw_package",
                return_value=package_dir,
            ) as mocked_refresh:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "refresh-openclaw-package",
                            "--output-dir",
                            str(package_dir),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_refresh.called)
            self.assertEqual(mocked_refresh.call_args.kwargs["output_dir"], package_dir)
            self.assertIn(str(package_dir), stdout.getvalue())

    def test_refresh_codex_package_command_uses_package_builder(self) -> None:
        with TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "codex-package"
            with patch(
                "tools.question_generator.cli.refresh_codex_package",
                return_value=package_dir,
            ) as mocked_refresh:
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(
                        [
                            "refresh-codex-package",
                            "--output-dir",
                            str(package_dir),
                        ]
                    )

            self.assertEqual(exit_code, 0)
            self.assertTrue(mocked_refresh.called)
            self.assertEqual(mocked_refresh.call_args.kwargs["output_dir"], package_dir)
            self.assertIn(str(package_dir), stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
