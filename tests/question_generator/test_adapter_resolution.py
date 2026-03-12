import unittest


from tools.question_generator.adapter_resolution import resolve_stage_modules
from tools.question_generator.contracts import load_contract
from tools.question_generator.pathing import adapters_dir, output_modes_dir


ROUTING = {
    "task": "Decide",
    "domain": "Investing / Markets",
    "output_mode": "Decision Memo",
    "evidence_mode": "Market-Tape / Price-Action-First",
    "uncertainty_mode": "Hidden-Variable Dominated",
    "decision_mode": "Portfolio Construction",
}


class AdapterResolutionTest(unittest.TestCase):
    def test_routing_stage_has_no_resolved_modules(self) -> None:
        contract = load_contract("routing")

        resolved = resolve_stage_modules(contract, ROUTING)

        self.assertEqual(resolved, {})

    def test_decision_logic_resolves_all_required_dimensions(self) -> None:
        contract = load_contract("decision_logic")

        resolved = resolve_stage_modules(contract, ROUTING)

        self.assertEqual(sorted(resolved.keys()), sorted(contract.depends_on))
        self.assertEqual(
            resolved["task"].path,
            adapters_dir() / "tasks" / "decide.md",
        )
        self.assertEqual(
            resolved["output_mode"].path,
            output_modes_dir() / "decision-memo.md",
        )


if __name__ == "__main__":
    unittest.main()
