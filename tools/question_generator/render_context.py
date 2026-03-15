from __future__ import annotations

import copy
from pathlib import Path

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
    output_mode = state["routing"]["output_mode"]
    context: dict[str, object] = {
        "topic": state.get("topic", ""),
        "routing": _build_routing_context(state["routing"]),
        "stage_guidance": _filter_render_stage_guidance(output_mode, stage_guidance),
        "required_output_schema": required_output_schema,
        "feedback_schema": feedback_schema,
        "render_mode": output_mode,
        "render_template_path": str(select_render_template(output_mode)),
    }
    context.update(_build_output_mode_context(output_mode, state))
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


def _build_output_mode_context(output_mode: str, state: dict) -> dict[str, object]:
    if output_mode == "Research Memo":
        return {
            "boundary": copy.deepcopy(state["boundary"]),
            "structure": copy.deepcopy(state["structure"]),
            "scenarios": copy.deepcopy(state["scenarios"]),
            "questions": copy.deepcopy(state["questions"]),
            "evidence_plan": copy.deepcopy(state["evidence_plan"]),
            "uncertainty_map": copy.deepcopy(state["uncertainty_map"]),
            "signals": copy.deepcopy(state["signals"]),
            "monitoring": _pick_fields(state["monitoring"], ["what_to_monitor_next"]),
            "decision_logic": _pick_fields(
                state["decision_logic"],
                ["appropriate_evidence_threshold", "triggers"],
            ),
        }

    if output_mode == "Decision Memo":
        return {
            "decision_logic": copy.deepcopy(state["decision_logic"]),
            "synthesis": copy.deepcopy(state["synthesis"]),
            "scenarios": copy.deepcopy(state["scenarios"]),
            "evidence_plan": _pick_fields(
                state["evidence_plan"],
                ["evidence_hierarchy", "question_to_evidence_mapping"],
            ),
            "uncertainty_map": copy.deepcopy(state["uncertainty_map"]),
            "questions": _pick_fields(state["questions"], ["top_killer_questions"]),
            "monitoring": _pick_fields(state["monitoring"], ["what_to_monitor_next"]),
        }

    if output_mode == "Monitoring Dashboard":
        return {
            "boundary": _pick_fields(state["boundary"], ["exact_object_of_analysis", "core_system"]),
            "scenarios": copy.deepcopy(state["scenarios"]),
            "monitoring": copy.deepcopy(state["monitoring"]),
            "signals": copy.deepcopy(state["signals"]),
            "evidence_plan": _pick_fields(state["evidence_plan"], ["evidence_hierarchy"]),
            "uncertainty_map": _pick_fields(state["uncertainty_map"], ["task_material_uncertainties"]),
            "decision_logic": _pick_fields(
                state["decision_logic"],
                [
                    "must_know_before_action",
                    "can_learn_after_action",
                    "appropriate_evidence_threshold",
                    "reversibility_logic",
                    "sizing_logic",
                    "staging_logic",
                    "triggers",
                    "hedge_exit_kill_criteria",
                ],
            ),
            "questions": _pick_fields(state["questions"], ["top_killer_questions"]),
        }

    if output_mode == "Scenario Tree":
        return {
            "boundary": _pick_fields(
                state["boundary"],
                ["exact_object_of_analysis", "core_system", "scope_assumptions"],
            ),
            "structure": _pick_fields(
                state["structure"],
                ["causal_mechanism", "killer_variables", "threshold_variables"],
            ),
            "scenarios": copy.deepcopy(state["scenarios"]),
            "evidence_plan": _pick_fields(
                state["evidence_plan"],
                ["question_to_evidence_mapping"],
            ),
            "monitoring": _pick_fields(state["monitoring"], ["what_to_monitor_next"]),
            "signals": _pick_fields(
                {"signals": state["signals"]},
                ["signals"],
            )["signals"],
            "questions": _pick_fields(state["questions"], ["top_killer_questions"]),
            "uncertainty_map": copy.deepcopy(state["uncertainty_map"]),
        }

    if output_mode == "Deep-Research Prompt":
        return {
            "boundary": copy.deepcopy(state["boundary"]),
            "structure": copy.deepcopy(state["structure"]),
            "scenarios": copy.deepcopy(state["scenarios"]),
            "questions": copy.deepcopy(state["questions"]),
            "evidence_plan": copy.deepcopy(state["evidence_plan"]),
            "monitoring": _pick_fields(state["monitoring"], ["what_to_monitor_next"]),
            "decision_logic": _pick_fields(state["decision_logic"], ["triggers"]),
            "uncertainty_map": copy.deepcopy(state["uncertainty_map"]),
        }

    if output_mode == "Investment Worksheet":
        return {
            "boundary": _pick_fields(state["boundary"], ["exact_object_of_analysis", "core_system"]),
            "structure": copy.deepcopy(state["structure"]),
            "scenarios": copy.deepcopy(state["scenarios"]),
            "questions": _pick_fields(state["questions"], ["top_killer_questions"]),
            "evidence_plan": _pick_fields(
                state["evidence_plan"],
                ["evidence_hierarchy", "question_to_evidence_mapping"],
            ),
            "decision_logic": copy.deepcopy(state["decision_logic"]),
            "synthesis": copy.deepcopy(state["synthesis"]),
            "signals": copy.deepcopy(state["signals"]),
            "monitoring": _pick_fields(state["monitoring"], ["what_to_monitor_next"]),
            "uncertainty_map": _pick_fields(state["uncertainty_map"], ["task_material_uncertainties"]),
        }

    raise ValueError(f"Unsupported render output mode: {output_mode!r}")


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


def _pick_fields(section: dict, fields: list[str]) -> dict:
    return {field: copy.deepcopy(section[field]) for field in fields if field in section}
