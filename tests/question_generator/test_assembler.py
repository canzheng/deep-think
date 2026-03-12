import unittest


from tools.question_generator.assembler import assemble_stage_prompt


STATE = {
    "topic": "Should we add to NVDA ahead of earnings?",
    "routing": {
        "task": "Decide",
        "domain": "Investing / Markets",
        "output_mode": "Decision Memo",
        "evidence_mode": "Market-Tape / Price-Action-First",
        "uncertainty_mode": "Hidden-Variable Dominated",
        "decision_mode": "Portfolio Construction",
    },
    "boundary": {"core_system": "NVIDIA earnings setup"},
    "structure": {"bottlenecks": ["datacenter demand durability"]},
    "scenarios": {"base_case": {"summary": "base"}},
    "questions": {"top_killer_questions": [{"question": "Is demand pull-forward?"}]},
    "evidence_plan": {"evidence_hierarchy": ["guidance", "revisions"]},
    "uncertainty_map": {"irreducible_uncertainties": ["management tone"]},
    "decision_logic": {"must_know_before_action": ["position sizing"]},
    "synthesis": {"recommendation_or_action_frame": "small add"},
    "signals": [{"signal": "estimate revisions"}],
    "monitoring": {"what_to_watch": [{"item": "estimate revisions"}]},
}


class AssemblerTest(unittest.TestCase):
    def test_question_generation_prompt_contains_all_core_sections(self) -> None:
        prompt = assemble_stage_prompt(
            "question_generation",
            STATE,
            optional_reads=["boundary"],
        )

        self.assertIn("## Stage 5 - Question Generation", prompt)
        self.assertIn("## Current State", prompt)
        self.assertIn("## Active Steering", prompt)
        self.assertIn("## Required Output", prompt)
        self.assertIn("## Feedback", prompt)
        self.assertIn("Because this is a `Decide` task", prompt)
        self.assertIn('"required": [', prompt)

    def test_render_prompt_uses_full_state_and_no_feedback(self) -> None:
        prompt = assemble_stage_prompt("render", STATE)

        self.assertIn("## Stage 10 - Render", prompt)
        self.assertIn("### The current monitoring layer is:", prompt)
        self.assertNotIn("## Feedback", prompt)


if __name__ == "__main__":
    unittest.main()
