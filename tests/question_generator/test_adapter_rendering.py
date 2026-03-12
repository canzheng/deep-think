import unittest


from tools.question_generator.adapter_rendering import render_adapter_sections
from tools.question_generator.adapter_resolution import resolve_stage_modules
from tools.question_generator.contracts import load_contract


ROUTING = {
    "task": "Decide",
    "domain": "Investing / Markets",
    "output_mode": "Decision Memo",
    "evidence_mode": "Market-Tape / Price-Action-First",
    "uncertainty_mode": "Hidden-Variable Dominated",
    "decision_mode": "Portfolio Construction",
}


class AdapterRenderingTest(unittest.TestCase):
    def test_rendered_steering_uses_dimension_aware_wrappers(self) -> None:
        contract = load_contract("decision_logic")
        resolved = resolve_stage_modules(contract, ROUTING)

        rendered = render_adapter_sections("decision_logic", resolved)

        self.assertIn("## Active Steering", rendered)
        self.assertIn("Because this is a `Decide` task", rendered)
        self.assertIn("Because this problem sits in `Investing / Markets`", rendered)
        self.assertIn("Because the deliverable is `Decision Memo`", rendered)
        self.assertIn("Relevance: Primary", rendered)
        self.assertIn("action thresholds explicit", rendered)
        self.assertIn("Required sections:", rendered)


if __name__ == "__main__":
    unittest.main()
