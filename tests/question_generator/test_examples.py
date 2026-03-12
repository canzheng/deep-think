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


class ExampleAssemblyTest(unittest.TestCase):
    def test_decision_logic_example_contains_expected_modules_and_outputs(self) -> None:
        prompt = assemble_stage_prompt(
            "decision_logic",
            STATE,
            optional_reads=["structure", "question_generation"],
        )

        self.assertIn("## Stage 7 - Decision Logic", prompt)
        self.assertIn("Because this problem sits in `Investing / Markets`", prompt)
        self.assertIn("Because the action problem is `Portfolio Construction`", prompt)
        self.assertIn('"decision_logic"', prompt)
        self.assertIn('"synthesis"', prompt)


if __name__ == "__main__":
    unittest.main()
