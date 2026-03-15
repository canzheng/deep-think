import json
import tempfile
import unittest
from pathlib import Path


from tools.question_generator.contracts import load_contract, load_contract_file


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "prompt" / "question-generator" / "contracts"
STATE_SECTIONS_DIR = CONTRACTS_DIR / "state-sections"
SHARED_STATE_SCHEMA_PATH = CONTRACTS_DIR / "shared_state_schema.json"

CONTRACT_FILES = sorted(
    path.name
    for path in CONTRACTS_DIR.glob("*.json")
    if path.name != "shared_state_schema.json"
)

RENDER_CONTRACT = "10-render.contract.json"
REQUIRED_KEYS = {"stage", "depends_on", "writes", "output_format", "feedback"}
NON_RENDER_REQUIRED_KEYS = {"reads_required", "reads_optional"}
FEEDBACK_SCHEMA_REQUIRED = {
    "05-question-generation.contract.json",
    "06-evidence-planning.contract.json",
}
STATE_SECTION_FILES = {
    "topic": "topic.schema.json",
    "routing": "routing.schema.json",
    "boundary": "boundary.schema.json",
    "structure": "structure.schema.json",
    "scenarios": "scenarios.schema.json",
    "questions": "questions.schema.json",
    "evidence_plan": "evidence_plan.schema.json",
    "uncertainty_map": "uncertainty_map.schema.json",
    "decision_logic": "decision_logic.schema.json",
    "synthesis": "synthesis.schema.json",
    "signals": "signals.schema.json",
    "monitoring": "monitoring.schema.json",
}
STAGE_SECTION_REFS = {
    "01-routing.contract.json": {"routing": "./state-sections/routing.schema.json"},
    "02-boundary.contract.json": {"boundary": "./state-sections/boundary.schema.json"},
    "03-structure.contract.json": {"structure": "./state-sections/structure.schema.json"},
    "04-scenarios.contract.json": {"scenarios": "./state-sections/scenarios.schema.json"},
    "05-question-generation.contract.json": {"questions": "./state-sections/questions.schema.json"},
    "06-evidence-planning.contract.json": {
        "evidence_plan": "./state-sections/evidence_plan.schema.json",
        "uncertainty_map": "./state-sections/uncertainty_map.schema.json",
    },
    "07-decision-logic.contract.json": {
        "decision_logic": "./state-sections/decision_logic.schema.json",
        "synthesis": "./state-sections/synthesis.schema.json",
    },
    "08-signal-translation.contract.json": {"signals": "./state-sections/signals.schema.json"},
    "09-monitoring.contract.json": {"monitoring": "./state-sections/monitoring.schema.json"},
}


class ContractLoadingTest(unittest.TestCase):
    def load_payload(self, filename: str) -> dict:
        with (CONTRACTS_DIR / filename).open() as contract_file:
            return json.load(contract_file)

    def load_shared_state_schema(self) -> dict:
        with SHARED_STATE_SCHEMA_PATH.open() as schema_file:
            return json.load(schema_file)

    def test_stage_contracts_expose_required_schema_fields(self) -> None:
        for filename in CONTRACT_FILES:
            with self.subTest(contract=filename):
                payload = self.load_payload(filename)
                contract = load_contract(payload["stage"])

                self.assertTrue(REQUIRED_KEYS.issubset(contract.raw.keys()))
                self.assertEqual(contract.stage, payload["stage"])
                self.assertEqual(contract.depends_on, payload["depends_on"])
                self.assertEqual(contract.writes, payload["writes"])
                self.assertEqual(contract.output_format, payload["output_format"])
                self.assertIsNotNone(contract.output_schema)

                if filename != RENDER_CONTRACT:
                    self.assertTrue(NON_RENDER_REQUIRED_KEYS.issubset(contract.raw.keys()))
                    self.assertEqual(
                        contract.output_schema.required,
                        contract.writes,
                    )
                    self.assertEqual(
                        set(contract.output_schema.properties.keys()),
                        set(contract.writes),
                    )
                else:
                    self.assertEqual(contract.writes, [])
                    self.assertIsNotNone(contract.reads_required_common)
                    self.assertIsNotNone(contract.reads_by_output_mode)
                    self.assertIn("routing", contract.reads_required_common)
                    self.assertIn("Decision Memo", contract.reads_by_output_mode)
                    self.assertIn("decision_logic", contract.reads_by_output_mode["Decision Memo"])

                if filename in FEEDBACK_SCHEMA_REQUIRED:
                    self.assertIsNotNone(contract.feedback.schema)

    def test_shared_state_schema_uses_section_refs(self) -> None:
        payload = self.load_shared_state_schema()

        self.assertEqual(payload["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(payload["type"], "object")
        self.assertEqual(payload["additionalProperties"], False)
        self.assertEqual(set(payload["required"]), set(STATE_SECTION_FILES))
        self.assertEqual(set(payload["properties"]), set(STATE_SECTION_FILES))

        for section_name, filename in STATE_SECTION_FILES.items():
            with self.subTest(section=section_name):
                self.assertEqual(
                    payload["properties"][section_name]["$ref"],
                    f"./state-sections/{filename}",
                )
                self.assertTrue((STATE_SECTIONS_DIR / filename).is_file())

    def test_stage_contract_output_schemas_preserve_section_refs(self) -> None:
        for contract_name, expected_refs in STAGE_SECTION_REFS.items():
            with self.subTest(contract=contract_name):
                payload = self.load_payload(contract_name)
                output_schema = payload["output_schema"]
                self.assertEqual(output_schema["type"], "object")
                self.assertEqual(set(output_schema["required"]), set(expected_refs))

                for property_name, ref_path in expected_refs.items():
                    self.assertEqual(
                        output_schema["properties"][property_name]["$ref"],
                        ref_path,
                    )

    def test_routing_schema_requires_primary_fields_but_allows_missing_secondary_fields(self) -> None:
        payload = self.load_payload("shared_state_schema.json")
        routing_schema_ref = payload["properties"]["routing"]["$ref"]
        routing_schema_path = CONTRACTS_DIR / routing_schema_ref.removeprefix("./")
        with routing_schema_path.open() as schema_file:
            routing_schema = json.load(schema_file)

        required_fields = set(routing_schema["required"])
        self.assertIn("task", required_fields)
        self.assertIn("domain", required_fields)
        self.assertIn("output_mode", required_fields)
        self.assertIn("evidence_mode", required_fields)
        self.assertIn("uncertainty_mode", required_fields)
        self.assertIn("decision_mode", required_fields)
        self.assertNotIn("secondary_task", required_fields)
        self.assertNotIn("secondary_domain", required_fields)
        self.assertNotIn("secondary_output_mode", required_fields)
        self.assertNotIn("secondary_evidence_mode", required_fields)
        self.assertNotIn("secondary_uncertainty_mode", required_fields)
        self.assertNotIn("secondary_decision_mode", required_fields)

        rationale_required = set(
            routing_schema["properties"]["classification_rationales"]["required"]
        )
        self.assertIn("task", rationale_required)
        self.assertIn("domain", rationale_required)
        self.assertIn("output_mode", rationale_required)
        self.assertIn("evidence_mode", rationale_required)
        self.assertIn("uncertainty_mode", rationale_required)
        self.assertIn("decision_mode", rationale_required)
        self.assertNotIn("secondary_task", rationale_required)
        self.assertNotIn("secondary_domain", rationale_required)
        self.assertNotIn("secondary_output_mode", rationale_required)
        self.assertNotIn("secondary_evidence_mode", rationale_required)
        self.assertNotIn("secondary_uncertainty_mode", rationale_required)
        self.assertNotIn("secondary_decision_mode", rationale_required)

    def test_loader_returns_parsed_contract_model(self) -> None:
        contract = load_contract("question_generation")

        self.assertEqual(contract.stage, "question_generation")
        self.assertEqual(contract.writes, ["questions"])
        self.assertEqual(
            contract.output_schema.required,
            ["questions"],
        )
        self.assertTrue(contract.feedback.supported)

    def test_loader_rejects_contract_missing_required_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            contract_path = Path(temp_dir) / "bad.contract.json"
            contract_path.write_text(
                json.dumps(
                    {
                        "stage": "routing",
                        "writes": ["routing"],
                    }
                )
            )

            with self.assertRaises(ValueError):
                load_contract_file(contract_path)


if __name__ == "__main__":
    unittest.main()
