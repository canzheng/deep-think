import os
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


from tools.question_generator.openclaw_package import (
    PACKAGE_RUNTIME_ROOT_ENV_VAR,
    build_openclaw_package,
    default_openclaw_package_dir,
)
from tools.question_generator.pathing import contract_path, repo_root, stage_template_path


class OpenClawPackageTest(unittest.TestCase):
    def test_default_openclaw_package_dir_points_at_skill_bundle(self) -> None:
        package_dir = default_openclaw_package_dir()

        self.assertEqual(
            package_dir,
            Path(__file__).resolve().parents[2] / "skills" / "deep-think" / "openclaw",
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

    def test_build_openclaw_package_copies_runtime_assets_config_and_vendor_dependency(self) -> None:
        with TemporaryDirectory() as tmpdir:
            package_dir = build_openclaw_package(output_dir=Path(tmpdir) / "bundle")

            self.assertTrue((package_dir / "SKILL.md").is_file())
            self.assertTrue((package_dir / "config" / "runtime.json").is_file())
            self.assertTrue((package_dir / "runtime" / "tools" / "question_generator" / "cli.py").is_file())
            self.assertTrue(
                (package_dir / "runtime" / "prompt" / "question-generator" / "contracts" / "01-routing.contract.json").is_file()
            )
            self.assertTrue((package_dir / "vendor" / "chevron" / "chevron" / "__init__.py").is_file())
            self.assertTrue((package_dir / "scripts" / "init_topic_run.py").is_file())
            self.assertTrue((package_dir / "scripts" / "prepare_stage.py").is_file())
            self.assertTrue((package_dir / "scripts" / "apply_response.py").is_file())
            self.assertTrue((package_dir / "scripts" / "run_topic.py").is_file())
            runtime_config = json.loads((package_dir / "config" / "runtime.json").read_text(encoding="utf-8"))
            self.assertEqual(runtime_config, {"json_executor": "session"})

    def test_openclaw_scripts_reference_bundled_runtime(self) -> None:
        with TemporaryDirectory() as tmpdir:
            package_dir = build_openclaw_package(output_dir=Path(tmpdir) / "bundle")

            init_topic_run = (package_dir / "scripts" / "init_topic_run.py").read_text(encoding="utf-8")
            prepare_stage = (package_dir / "scripts" / "prepare_stage.py").read_text(encoding="utf-8")
            apply_response = (package_dir / "scripts" / "apply_response.py").read_text(encoding="utf-8")

            self.assertIn('os.environ.setdefault("QUESTION_GENERATOR_RUNTIME_ROOT"', init_topic_run)
            self.assertIn('os.environ.setdefault("QUESTION_GENERATOR_OPENCLAW_CONFIG_PATH"', init_topic_run)
            self.assertIn('raise SystemExit(main(["init-topic-run", *sys.argv[1:]]))', init_topic_run)
            self.assertIn('raise SystemExit(main(["prepare-stage", *sys.argv[1:]]))', prepare_stage)
            self.assertIn('raise SystemExit(main(["apply-response", *sys.argv[1:]]))', apply_response)

    def test_openclaw_runtime_config_is_gitignored(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(
            "skills/deep-think/openclaw/config/runtime.json",
            gitignore,
            msg="expected runtime config path to be gitignored",
        )


if __name__ == "__main__":
    unittest.main()
