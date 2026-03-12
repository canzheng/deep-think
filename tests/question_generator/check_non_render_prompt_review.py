from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.question_generator.assemble_non_render_prompts import NON_RENDER_STAGES

TESTS_DIR = REPO_ROOT / "tests" / "question_generator"
REVIEW_SCHEMA_PATH = TESTS_DIR / "non_render_prompt_review_schema.json"

VALID_HARD_GATE_VALUES = {"PASS", "FAIL"}
VALID_RECOMMENDATIONS = {
    "Accept",
    "Accept with minor improvements",
    "Needs revision",
}
VALID_STAGES = set(NON_RENDER_STAGES)
REQUIRED_HARD_GATES = (
    "instruction_coherence",
    "input_precedence_clarity",
    "output_requirement_clarity",
    "sufficient_starting_context",
)
REQUIRED_SCORES = (
    "task_clarity",
    "context_usefulness",
    "guidance_and_constraint_clarity",
    "readability",
    "output_readiness",
    "confidence_to_execute",
    "context_efficiency",
    "risk_of_misinterpretation",
)


def load_review_schema() -> dict:
    with REVIEW_SCHEMA_PATH.open() as schema_file:
        return json.load(schema_file)


def _unexpected_keys(payload: dict, expected_keys: set[str], label: str) -> list[str]:
    extras = sorted(set(payload.keys()) - expected_keys)
    if not extras:
        return []
    return [f"{label} has unexpected keys: {', '.join(extras)}"]


def validate_review_payload(payload: dict) -> list[str]:
    errors: list[str] = []

    if not isinstance(payload, dict):
        return ["payload must be an object"]

    errors.extend(
        _unexpected_keys(
            payload,
            {
                "stage",
                "hard_gates",
                "scores",
                "top_findings",
                "overall_recommendation",
                "summary",
            },
            "payload",
        )
    )

    if payload.get("stage") not in VALID_STAGES:
        errors.append("stage must be one of the supported non-render stages")

    hard_gates = payload.get("hard_gates")
    if not isinstance(hard_gates, dict):
        errors.append("hard_gates must be an object")
    else:
        errors.extend(
            _unexpected_keys(
                hard_gates,
                set(REQUIRED_HARD_GATES),
                "hard_gates",
            )
        )
        missing = [key for key in REQUIRED_HARD_GATES if key not in hard_gates]
        if missing:
            errors.append(f"hard_gates missing required keys: {', '.join(missing)}")
        for key in REQUIRED_HARD_GATES:
            value = hard_gates.get(key)
            if value is not None and value not in VALID_HARD_GATE_VALUES:
                errors.append(f"hard_gates.{key} must be PASS or FAIL")

    scores = payload.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores must be an object")
    else:
        errors.extend(
            _unexpected_keys(
                scores,
                set(REQUIRED_SCORES),
                "scores",
            )
        )
        missing = [key for key in REQUIRED_SCORES if key not in scores]
        if missing:
            errors.append(f"scores missing required keys: {', '.join(missing)}")
        for key in REQUIRED_SCORES:
            value = scores.get(key)
            if value is None:
                continue
            if type(value) is not int or not 1 <= value <= 5:
                errors.append(f"scores.{key} must be an integer from 1 to 5")

    top_findings = payload.get("top_findings")
    if not isinstance(top_findings, list):
        errors.append("top_findings must be an array")
    else:
        for index, finding in enumerate(top_findings):
            if not isinstance(finding, dict):
                errors.append(f"top_findings[{index}] must be an object")
                continue
            errors.extend(
                _unexpected_keys(
                    finding,
                    {"title", "why_it_matters", "prompt_evidence"},
                    f"top_findings[{index}]",
                )
            )
            for key in ("title", "why_it_matters", "prompt_evidence"):
                if not isinstance(finding.get(key), str) or not finding.get(key):
                    errors.append(f"top_findings[{index}].{key} must be a non-empty string")

    recommendation = payload.get("overall_recommendation")
    if recommendation not in VALID_RECOMMENDATIONS:
        errors.append("overall_recommendation must be a supported recommendation")

    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("summary must be a non-empty string")

    return errors


def review_passes_hard_gates(payload: dict) -> bool:
    hard_gates = payload.get("hard_gates", {})
    return all(hard_gates.get(key) == "PASS" for key in REQUIRED_HARD_GATES)


def load_review_results(path: Path) -> list[dict]:
    with path.open() as input_file:
        payload = json.load(input_file)

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("reviews"), list):
        return payload["reviews"]
    raise ValueError("review input must be a JSON array or an object with a 'reviews' array")


def format_review_report(results: list[dict]) -> str:
    lines: list[str] = []
    for payload in results:
        hard_gates = payload["hard_gates"]
        scores = payload["scores"]
        lines.extend(
            [
                f"Stage: {payload['stage']}",
                "  Hard gates: "
                + " ".join(
                    [
                        hard_gates["instruction_coherence"],
                        hard_gates["input_precedence_clarity"],
                        hard_gates["output_requirement_clarity"],
                        hard_gates["sufficient_starting_context"],
                    ]
                ),
                "  Scores: "
                + " ".join(
                    [
                        f"task={scores['task_clarity']}",
                        f"context={scores['context_usefulness']}",
                        f"guidance={scores['guidance_and_constraint_clarity']}",
                        f"readability={scores['readability']}",
                        f"output={scores['output_readiness']}",
                        f"confidence={scores['confidence_to_execute']}",
                        f"efficiency={scores['context_efficiency']}",
                        f"misread_risk={scores['risk_of_misinterpretation']}",
                    ]
                ),
                f"  Recommendation: {payload['overall_recommendation']}",
            ]
        )
    return "\n".join(lines)


def validate_review_results(results: list[object]) -> list[str]:
    errors: list[str] = []
    seen_stages: list[str] = []

    for index, payload in enumerate(results):
        payload_errors = validate_review_payload(payload)
        if payload_errors:
            errors.extend([f"reviews[{index}]: {error}" for error in payload_errors])
            continue
        assert isinstance(payload, dict)
        seen_stages.append(payload["stage"])

    missing = [stage for stage in NON_RENDER_STAGES if stage not in seen_stages]
    duplicates = sorted({stage for stage in seen_stages if seen_stages.count(stage) > 1})
    if missing:
        errors.append(f"review set missing stages: {', '.join(missing)}")
    if duplicates:
        errors.append(f"review set has duplicate stages: {', '.join(duplicates)}")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate structured non-render prompt review results."
    )
    parser.add_argument("--input", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = load_review_results(Path(args.input))

    validation_errors = validate_review_results(results)
    hard_gate_failure = False
    valid_results: list[dict] = []
    for payload in results:
        if validate_review_payload(payload):
            continue
        assert isinstance(payload, dict)
        valid_results.append(payload)
        if not review_passes_hard_gates(payload):
            hard_gate_failure = True

    if validation_errors:
        for error in validation_errors:
            print(f"Validation error: {error}")
    if valid_results:
        print(format_review_report(valid_results))

    if validation_errors or hard_gate_failure:
        print("QUALITY REVIEW FAIL")
        return 1

    print("QUALITY REVIEW PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
