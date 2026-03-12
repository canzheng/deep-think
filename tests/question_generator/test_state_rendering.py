import unittest


from tools.question_generator.state_rendering import render_state_sections


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

        self.assertIn("## Current State", rendered)
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


if __name__ == "__main__":
    unittest.main()
