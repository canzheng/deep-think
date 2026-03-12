import json
import unittest
from pathlib import Path


from tools.question_generator.state_rendering import render_state_sections


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
POPULATED_STATE_PATH = FIXTURES_DIR / "populated_state.json"


def load_populated_state() -> dict:
    with POPULATED_STATE_PATH.open() as fixture_file:
        return json.load(fixture_file)


class StateRenderingTest(unittest.TestCase):
    def test_rendered_state_uses_readable_section_headings(self) -> None:
        rendered = render_state_sections(
            "decision_logic",
            {
                "routing": {"task": "Decide"},
                "structure": {"bottlenecks": ["supply"]},
                "scenarios": {"base_case": {"summary": "base"}},
            },
        )

        self.assertIn("## Relevant Context", rendered)
        self.assertNotIn("## Current State", rendered)
        self.assertIn("### The current routing for this run is:", rendered)
        self.assertIn("### The current structural view of the system is:", rendered)
        self.assertIn("```json", rendered)

    def test_render_stage_full_state_rendering_includes_monitoring(self) -> None:
        rendered = render_state_sections(
            "render",
            {
                "routing": {"task": "Decide"},
                "monitoring": {"what_to_watch": [{"item": "revisions"}]},
            },
        )

        self.assertIn("### The current routing for this run is:", rendered)
        self.assertIn("### The current monitoring layer is:", rendered)

    def test_routing_renderer_surfaces_human_meaningful_context(self) -> None:
        state = load_populated_state()

        rendered = render_state_sections(
            "decision_logic",
            {"routing": state["routing"]},
        )

        self.assertIn("Should we stage an expansion of the Atlas forecasting product", rendered)
        self.assertIn("Company / Product Strategy", rendered)
        self.assertIn("Decision Memo", rendered)
        self.assertIn("next 2 quarters", rendered)
        self.assertIn("one staged product rollout into a regulated segment", rendered)
        self.assertIn("The company can run a limited pilot before broad release.", rendered)
        self.assertNotIn("adapter", rendered.lower())
        self.assertNotIn("module", rendered.lower())
        self.assertNotIn("selection", rendered.lower())

    def test_unknown_sections_fall_back_to_json_rendering(self) -> None:
        rendered = render_state_sections(
            "decision_logic",
            {"custom_section": {"foo": "bar"}},
        )

        self.assertIn("### Current custom_section:", rendered)
        self.assertIn("```json", rendered)
        self.assertIn('"foo": "bar"', rendered)

    def test_specialized_renderers_include_key_summary_fields(self) -> None:
        state = load_populated_state()

        rendered = render_state_sections(
            "render",
            {
                "structure": state["structure"],
                "scenarios": state["scenarios"],
                "questions": state["questions"],
                "decision_logic": state["decision_logic"],
                "monitoring": state["monitoring"],
            },
        )

        self.assertIn("- Stakeholders:", rendered)
        self.assertIn("product leadership", rendered)
        self.assertIn("- Base case:", rendered)
        self.assertIn("Measured pilot success", rendered)
        self.assertIn("- Top killer questions:", rendered)
        self.assertIn("What exact workflow is Atlas improving for the pilot customers?", rendered)
        self.assertIn("- Evidence threshold:", rendered)
        self.assertIn("Approve only a narrow pilot until workflow gains are demonstrated", rendered)
        self.assertIn("- What to watch:", rendered)
        self.assertIn("weekly pilot retention after onboarding", rendered)
        self.assertNotIn("adapter", rendered.lower())
        self.assertEqual(
            rendered,
            render_state_sections(
                "render",
                {
                    "structure": state["structure"],
                    "scenarios": state["scenarios"],
                    "questions": state["questions"],
                    "decision_logic": state["decision_logic"],
                    "monitoring": state["monitoring"],
                },
            ),
        )


if __name__ == "__main__":
    unittest.main()
