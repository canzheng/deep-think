import unittest


from tools.question_generator.contracts import load_contract
from tools.question_generator.render_context import build_render_context
from tools.question_generator.state_resolution import resolve_state_sections


STATE = {
    "topic": "Should we add to NVDA ahead of earnings?",
    "routing": {"task": "Decide", "output_mode": "Decision Memo"},
    "boundary": {"core_system": "NVIDIA earnings setup"},
    "structure": {"bottlenecks": ["datacenter demand durability"]},
    "scenarios": {"base_case": {"summary": "In-line print"}},
    "questions": {"top_killer_questions": [{"question": "Is demand pull-forward?"}]},
    "evidence_plan": {"evidence_hierarchy": ["guidance", "revisions"]},
    "uncertainty_map": {"irreducible_uncertainties": ["management tone"]},
    "decision_logic": {"must_know_before_action": ["position sizing"]},
    "synthesis": {"recommendation_or_action_frame": "small add"},
    "signals": [{"signal": "estimate revisions"}],
    "monitoring": {"what_to_watch": [{"item": "estimate revisions"}]},
}


class StateResolutionTest(unittest.TestCase):
    def test_question_generation_uses_required_and_selected_optional_sections(self) -> None:
        contract = load_contract("question_generation")

        resolved = resolve_state_sections(contract, STATE, optional_reads=["boundary"])

        self.assertEqual(
            list(resolved.keys()),
            ["routing", "structure", "scenarios", "boundary"],
        )

    def test_evidence_planning_maps_question_generation_to_questions(self) -> None:
        contract = load_contract("evidence_planning")

        resolved = resolve_state_sections(contract, STATE)

        self.assertEqual(
            list(resolved.keys()),
            ["routing", "structure", "scenarios", "questions"],
        )
        self.assertEqual(resolved["questions"], STATE["questions"])

    def test_decision_logic_optional_question_generation_maps_to_questions(self) -> None:
        contract = load_contract("decision_logic")

        resolved = resolve_state_sections(contract, STATE, optional_reads=["question_generation"])

        self.assertIn("questions", resolved)
        self.assertEqual(resolved["questions"], STATE["questions"])

    def test_render_contract_is_not_supported_by_state_resolution_helper(self) -> None:
        contract = load_contract("render")

        with self.assertRaisesRegex(
            ValueError,
            "Render prompt assembly no longer uses state section resolution.",
        ):
            resolve_state_sections(contract, STATE)

    def test_render_context_uses_contract_declared_reads_instead_of_state_resolution_helper(self) -> None:
        context = build_render_context(
            STATE,
            stage_guidance={"required": [], "conditional": []},
            required_output_schema="",
            feedback_schema="",
        )

        self.assertIn("routing", context)
        self.assertIn("decision_logic", context)
        self.assertIn("synthesis", context)
        self.assertIn("questions", context)
        self.assertIn("monitoring", context)
        self.assertNotIn("boundary", context)
        self.assertNotIn("structure", context)


if __name__ == "__main__":
    unittest.main()
