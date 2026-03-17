from __future__ import annotations

import json
from pathlib import Path

from tools.question_generator.models import Feedback, OptionalRead, OutputSchema, StageContract
from tools.question_generator.pathing import contract_path


REQUIRED_CONTRACT_KEYS = {
    "stage",
    "depends_on",
    "writes",
    "output_format",
    "feedback",
    "output_schema",
}


def load_contract(stage: str) -> StageContract:
    return load_contract_file(contract_path(stage))


def load_contract_file(path: Path) -> StageContract:
    with path.open() as contract_file:
        payload = json.load(contract_file)

    missing_keys = REQUIRED_CONTRACT_KEYS - payload.keys()
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Contract {path} is missing required keys: {missing}")

    output_schema = payload["output_schema"]
    feedback = payload["feedback"]

    return StageContract(
        stage=payload["stage"],
        depends_on=payload["depends_on"],
        writes=payload["writes"],
        output_format=payload["output_format"],
        feedback=Feedback(
            supported=feedback["supported"],
            field=feedback.get("field"),
            schema=feedback.get("schema"),
        ),
        output_schema=OutputSchema(
            type=output_schema["type"],
            required=output_schema["required"],
            properties=output_schema["properties"],
            raw=output_schema,
        ),
        reads_required=payload.get("reads_required"),
        reads_optional=[
            OptionalRead(
                stage=item["stage"],
                kind=item["kind"],
                when=item["when"],
            )
            for item in payload.get("reads_optional", [])
        ],
        reads_required_common=payload.get("reads_required_common"),
        reads_by_output_mode=payload.get("reads_by_output_mode"),
        raw=payload,
    )
