import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from tools.question_generator.codex_package import (
    PACKAGE_RUNTIME_ROOT_ENV_VAR,
    build_codex_package,
    default_codex_package_dir,
)
from tools.question_generator.pathing import contract_path, repo_root, stage_template_path


class CodexPackageTest(unittest.TestCase):
    def test_default_codex_package_dir_points_at_skill_bundle(self) -> None:
        package_dir = default_codex_package_dir()

        self.assertEqual(
            package_dir,
            Path(__file__).resolve().parents[2] / "skills" / "deep-think" / "codex",
        )

    def test_runtime_root_env_override_repoints_pathing_helpers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            runtime_root = Path(tmpdir)
            resolved_runtime_root = runtime_root.resolve()
            (runtime_root / "prompt" / "question-generator" / "contracts").mkdir(parents=True, exist_ok=True)
            (runtime_root / "prompt" / "question-generator" / "stages").mkdir(parents=True, exist_ok=True)

            with patch.dict(os.environ, {PACKAGE_RUNTIME_ROOT_ENV_VAR: str(runtime_root)}, clear=False):
                self.assertEqual(repo_root(), resolved_runtime_root)
                self.assertEqual(
                    contract_path("routing"),
                    resolved_runtime_root / "prompt" / "question-generator" / "contracts" / "01-routing.contract.json",
                )
                self.assertEqual(
                    stage_template_path("render"),
                    resolved_runtime_root / "prompt" / "question-generator" / "stages" / "10-render.md",
                )

    def test_build_codex_package_copies_runtime_assets_and_vendor_dependency(self) -> None:
        with TemporaryDirectory() as tmpdir:
            package_dir = build_codex_package(output_dir=Path(tmpdir) / "bundle")

            self.assertTrue((package_dir / "SKILL.md").is_file())
            self.assertTrue((package_dir / "runtime" / "tools" / "question_generator" / "cli.py").is_file())
            self.assertTrue(
                (package_dir / "runtime" / "prompt" / "question-generator" / "contracts" / "01-routing.contract.json").is_file()
            )
            self.assertTrue((package_dir / "vendor" / "chevron" / "chevron" / "__init__.py").is_file())
            self.assertTrue((package_dir / "scripts" / "init_topic_run.py").is_file())
            self.assertTrue((package_dir / "scripts" / "prepare_stage.py").is_file())
            self.assertTrue((package_dir / "scripts" / "apply_response.py").is_file())
            self.assertTrue((package_dir / "scripts" / "run_topic.py").is_file())
            self.assertTrue((package_dir / "scripts" / "update_routing.py").is_file())
            self.assertTrue((package_dir / "scripts" / "resume_run.py").is_file())

    def test_codex_scripts_reference_bundled_runtime(self) -> None:
        with TemporaryDirectory() as tmpdir:
            package_dir = build_codex_package(output_dir=Path(tmpdir) / "bundle")

            init_topic_run = (package_dir / "scripts" / "init_topic_run.py").read_text(encoding="utf-8")
            prepare_stage = (package_dir / "scripts" / "prepare_stage.py").read_text(encoding="utf-8")
            apply_response = (package_dir / "scripts" / "apply_response.py").read_text(encoding="utf-8")
            run_topic = (package_dir / "scripts" / "run_topic.py").read_text(encoding="utf-8")
            resume_run = (package_dir / "scripts" / "resume_run.py").read_text(encoding="utf-8")

            self.assertIn('os.environ.setdefault("QUESTION_GENERATOR_RUNTIME_ROOT"', init_topic_run)
            self.assertIn('raise SystemExit(main(["init-topic-run", *sys.argv[1:]]))', init_topic_run)
            self.assertIn('raise SystemExit(main(["prepare-stage", *sys.argv[1:]]))', prepare_stage)
            self.assertIn('raise SystemExit(main(["apply-response", *sys.argv[1:]]))', apply_response)
            self.assertIn('os.environ.setdefault("QUESTION_GENERATOR_RUNTIME_ROOT"', run_topic)
            self.assertIn(
                'DEFAULT_RECIPE = BASE_DIR / "runtime" / "prompt" / "question-generator" / "recipes" / "non-render.recipe.json"',
                run_topic,
            )
            self.assertIn('return ["run-topic", *args]', run_topic)
            self.assertIn('return ["run-recipe-on-run", *args]', resume_run)


if __name__ == "__main__":
    unittest.main()
