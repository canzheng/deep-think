import json
import unittest
from pathlib import Path

from tools.question_generator.pathing import STAGE_NAME_MAP
from tools.question_generator.render_context import RENDER_TEMPLATE_MAP


REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_ROOT = REPO_ROOT / "prompt" / "question-generator"
CONTRACTS_DIR = PROMPT_ROOT / "contracts"
ADAPTERS_DIR = PROMPT_ROOT / "adapters"
STAGE_GUIDANCE_SCHEMA_PATH = ADAPTERS_DIR / "schemas" / "stage-guidance.schema.json"


class DocumentationConsistencyTest(unittest.TestCase):
    def test_render_contract_covers_all_supported_render_output_modes(self) -> None:
        with (CONTRACTS_DIR / "10-render.contract.json").open() as contract_file:
            payload = json.load(contract_file)

        self.assertIn("reads_required_common", payload)
        self.assertIn("reads_by_output_mode", payload)
        self.assertEqual(
            set(payload["reads_by_output_mode"]),
            set(RENDER_TEMPLATE_MAP),
        )

    def test_adapter_stage_guidance_schema_uses_normalized_runtime_stage_ids(self) -> None:
        with STAGE_GUIDANCE_SCHEMA_PATH.open() as schema_file:
            payload = json.load(schema_file)

        self.assertEqual(
            set(payload["properties"]),
            set(STAGE_NAME_MAP),
        )
        self.assertEqual(
            payload["$defs"]["stageGuidanceEntry"]["properties"]["importance"]["enum"],
            ["Important", "Moderate", "Light", "None"],
        )


if __name__ == "__main__":
    unittest.main()
