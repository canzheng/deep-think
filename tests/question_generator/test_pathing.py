from pathlib import Path
import unittest


from tools.question_generator import pathing


class PathingTest(unittest.TestCase):
    def test_repo_root_resolves_from_module_location(self) -> None:
        self.assertEqual(
            pathing.repo_root(),
            Path(__file__).resolve().parents[2],
        )

    def test_stage_contract_and_template_paths_use_canonical_stage_names(self) -> None:
        for stage, contract_name, template_name in [
            ("Routing", "01-routing.contract.json", "01-routing.md"),
            ("Question Generation", "05-question-generation.contract.json", "05-question-generation.md"),
            ("Monitoring", "09-monitoring.contract.json", "09-monitoring.md"),
            ("Render", "10-render.contract.json", "10-render.md"),
        ]:
            with self.subTest(stage=stage):
                self.assertEqual(
                    pathing.contract_path(stage),
                    pathing.contracts_dir() / contract_name,
                )
                self.assertEqual(
                    pathing.stage_template_path(stage),
                    pathing.stages_dir() / template_name,
                )
                self.assertTrue(pathing.contract_path(stage).is_file())
                self.assertTrue(pathing.stage_template_path(stage).is_file())

    def test_adapter_path_normalizes_routed_values(self) -> None:
        self.assertEqual(
            pathing.adapter_family_dir("task"),
            pathing.adapters_dir() / "tasks",
        )
        self.assertEqual(
            pathing.adapter_family_dir("evidence_mode"),
            pathing.adapters_dir() / "evidence-modes",
        )
        self.assertEqual(
            pathing.adapter_path("task", "Decide"),
            pathing.adapters_dir() / "tasks" / "decide.json",
        )
        self.assertEqual(
            pathing.adapter_path("domain", "Investing / Markets"),
            pathing.adapters_dir() / "domains" / "investing-markets.json",
        )
        self.assertEqual(
            pathing.adapter_path("evidence_mode", "Market-Tape / Price-Action-First"),
            pathing.adapters_dir()
            / "evidence-modes"
            / "market-tape-price-action-first.json",
        )
        self.assertEqual(
            pathing.adapter_path("uncertainty_mode", "Hidden-Variable Dominated"),
            pathing.adapters_dir()
            / "uncertainty-modes"
            / "hidden-variable-dominated.json",
        )
        self.assertEqual(
            pathing.adapter_path("decision_mode", "Portfolio Construction"),
            pathing.adapters_dir()
            / "decision-modes"
            / "portfolio-construction.json",
        )

    def test_render_template_path_uses_runtime_render_subtemplates(self) -> None:
        render_template_path = pathing.render_template_path("Decision Memo")
        self.assertEqual(
            render_template_path,
            pathing.stages_dir() / "render" / "decision-memo.md",
        )
        self.assertTrue(render_template_path.is_file())

    def test_render_template_path_rejects_unknown_output_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported render output mode"):
            pathing.render_template_path("Unknown Mode")

    def test_adapters_directory_contains_only_json_modules(self) -> None:
        legacy_markdown_modules = sorted(
            path.relative_to(pathing.adapters_dir()).as_posix()
            for path in pathing.adapters_dir().rglob("*.md")
            if path.parent.name != "schemas"
        )

        self.assertEqual(legacy_markdown_modules, [])


if __name__ == "__main__":
    unittest.main()
