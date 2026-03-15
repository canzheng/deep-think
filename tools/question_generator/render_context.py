from __future__ import annotations

import copy
from pathlib import Path

from tools.question_generator.contracts import load_contract
from tools.question_generator.pathing import normalize_stage_name, output_modes_dir, stages_dir


RENDER_TEMPLATE_MAP = {
    "Research Memo": "research-memo.md",
    "Decision Memo": "decision-memo.md",
    "Monitoring Dashboard": "monitoring-dashboard.md",
    "Scenario Tree": "scenario-tree.md",
    "Deep-Research Prompt": "deep-research-prompt.md",
    "Investment Worksheet": "investment-worksheet.md",
}

RENDER_STAGE_GUIDANCE_POLICY = {
    "Research Memo": {
        "required": ["domain", "evidence_mode", "uncertainty_mode"],
        "conditional": {
            "decision_mode": (
                "Use this only if the memo should end with action implications "
                "rather than stop at explanation."
            ),
        },
    },
    "Decision Memo": {
        "required": ["decision_mode", "uncertainty_mode"],
        "conditional": {
            "evidence_mode": (
                "Use this only if the preferred proof style should change how "
                "high the evidence bar is presented."
            ),
        },
    },
    "Monitoring Dashboard": {
        "required": ["uncertainty_mode", "decision_mode"],
        "conditional": {
            "evidence_mode": (
                "Use this only if source quality or source lag should change "
                "cadence or escalation."
            ),
            "domain": (
                "Use this only if domain-specific monitoring patterns change "
                "what deserves attention."
            ),
        },
    },
    "Scenario Tree": {
        "required": ["uncertainty_mode", "decision_mode"],
        "conditional": {
            "domain": (
                "Use this only if domain-specific path structure or branch "
                "language should shape the tree."
            ),
        },
    },
    "Deep-Research Prompt": {
        "required": ["evidence_mode", "uncertainty_mode", "decision_mode"],
        "conditional": {
            "domain": (
                "Use this only if domain-specific ontology should change how "
                "the prompt frames mechanisms, actors, or evidence."
            ),
        },
    },
    "Investment Worksheet": {
        "required": ["evidence_mode", "uncertainty_mode", "decision_mode"],
        "conditional": {
            "domain": (
                "Use this only if domain-specific market structure or "
                "operating context changes the worksheet framing."
            ),
        },
    },
}


def select_render_template(output_mode: str) -> Path:
    try:
        filename = RENDER_TEMPLATE_MAP[output_mode]
    except KeyError as exc:
        supported = ", ".join(sorted(RENDER_TEMPLATE_MAP))
        raise ValueError(
            f"Unsupported render output mode: {output_mode!r}. Supported modes: {supported}"
        ) from exc

    return stages_dir() / "render" / filename


def render_wrapper_template() -> Path:
    return stages_dir() / "10-render.md"


def build_render_context(
    state: dict,
    *,
    stage_guidance: dict[str, list[dict[str, str]]],
    required_output_schema: str,
    feedback_schema: str,
) -> dict[str, object]:
    contract = load_contract("render")
    output_mode = state["routing"]["output_mode"]
    context: dict[str, object] = {
        "stage_guidance": _filter_render_stage_guidance(output_mode, stage_guidance),
        "required_output_schema": required_output_schema,
        "feedback_schema": feedback_schema,
        "render_mode": output_mode,
        "render_template_path": str(select_render_template(output_mode)),
    }
    context.update(
        _build_render_reads_context(
            state=state,
            read_names=contract.reads_required_common or [],
        )
    )
    context.update(
        _build_render_reads_context(
            state=state,
            read_names=(contract.reads_by_output_mode or {}).get(output_mode, []),
        )
    )
    return context


def _build_routing_context(routing: dict) -> dict:
    allowed_fields = [
        "question",
        "explicit_constraints",
        "desired_output",
        "decision_context",
        "risk_tolerance",
        "time_horizon",
        "unit_of_analysis",
        "assumptions",
        "task",
        "domain",
        "output_mode",
        "evidence_mode",
        "uncertainty_mode",
        "decision_mode",
    ]
    return {field: copy.deepcopy(routing.get(field)) for field in allowed_fields if field in routing}


def _build_render_reads_context(
    *,
    state: dict,
    read_names: list[str],
) -> dict[str, object]:
    context: dict[str, object] = {}
    for read_name in read_names:
        key = _render_read_to_state_key(read_name)
        if key == "topic":
            context["topic"] = state.get("topic", "")
            continue
        if key == "routing":
            context["routing"] = _build_routing_context(state.get("routing", {}))
            continue
        if key in state:
            context[key] = copy.deepcopy(state[key])
    return context


def _render_read_to_state_key(read_name: str) -> str:
    if read_name == "evidence_planning":
        return "evidence_plan"
    return normalize_stage_name(read_name)


def _filter_render_stage_guidance(
    output_mode: str,
    stage_guidance: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, str]]]:
    policy = RENDER_STAGE_GUIDANCE_POLICY[output_mode]
    required_dimensions = set(policy["required"])
    conditional_dimensions = policy["conditional"]
    filtered = {"required": [], "conditional": []}

    for entry in stage_guidance.get("required", []) + stage_guidance.get("conditional", []):
        dimension = entry["dimension"]
        if dimension in required_dimensions:
            filtered["required"].append(copy.deepcopy(entry))
            continue

        condition = conditional_dimensions.get(dimension)
        if condition:
            filtered["conditional"].append({**copy.deepcopy(entry), "condition": condition})

    return filtered
