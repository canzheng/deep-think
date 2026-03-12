import json
import tempfile
import unittest
from pathlib import Path


from tools.question_generator.contracts import load_contract, load_contract_file


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "prompt" / "question-generator" / "contracts"

CONTRACT_FILES = sorted(
    path.name
    for path in CONTRACTS_DIR.glob("*.json")
    if path.name != "shared_state_schema.json"
)

RENDER_CONTRACT = "10-renderer.contract.json"
REQUIRED_KEYS = {"stage", "depends_on", "writes", "output_format", "feedback"}
NON_RENDER_REQUIRED_KEYS = {"reads_required", "reads_optional"}
FEEDBACK_SCHEMA_REQUIRED = {
    "05-question-generation.contract.json",
    "06-evidence-planning.contract.json",
}


class ContractLoadingTest(unittest.TestCase):
    def load_payload(self, filename: str) -> dict:
        with (CONTRACTS_DIR / filename).open() as contract_file:
            return json.load(contract_file)

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
                    self.assertEqual(
                        contract.output_schema.required,
                        ["deliverable"],
                    )
                    self.assertIn("deliverable", contract.output_schema.properties)
                    deliverable = contract.output_schema.properties["deliverable"]
                    self.assertEqual(
                        deliverable["properties"]["uses_shared_state_as_sole_analysis_input"]["const"],
                        True,
                    )
                    self.assertEqual(
                        deliverable["properties"]["must_not_write_state"]["const"],
                        True,
                    )

                if filename in FEEDBACK_SCHEMA_REQUIRED:
                    self.assertIsNotNone(contract.feedback.schema)

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
