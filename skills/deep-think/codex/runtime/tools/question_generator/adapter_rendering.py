from __future__ import annotations

from tools.question_generator.adapter_models import load_adapter_payload
from tools.question_generator.models import ResolvedModule
from tools.question_generator.pathing import normalize_stage_name


WRAPPER_TEMPLATES = {
    "task": "Because this is a `{value}` task, follow this guidance:",
    "domain": "Because this problem sits in `{value}`, follow this guidance:",
    "evidence_mode": "Because the preferred evidence mode is `{value}`, follow this guidance:",
    "uncertainty_mode": "Because the dominant uncertainty is `{value}`, follow this guidance:",
    "decision_mode": "Because the action problem is `{value}`, follow this guidance:",
    "output_mode": "Because the deliverable is `{value}`, follow this guidance:",
}

STAGE_GUIDANCE_POLICY = {
    "routing": {"required": [], "conditional": {}},
    "boundary": {
        "required": ["task", "domain"],
        "conditional": {
            "output_mode": "Use this only if the deliverable shape meaningfully narrows or widens scope.",
            "uncertainty_mode": "Use this only if hidden drivers or regime shifts may require a wider scope.",
            "decision_mode": "Use this only if the exact object of action changes under portfolio, adversarial, or staged-commitment reasoning.",
        },
    },
    "structure": {
        "required": ["task", "domain"],
        "conditional": {
            "uncertainty_mode": "Use this only if hidden drivers, deception, regime shift, sparse data, or noise should change structural confidence.",
            "decision_mode": "Use this only if the structure must include portfolio, countermove, or staged-commitment logic.",
            "evidence_mode": "Use this only if structural claims should be disciplined by the preferred proof style.",
        },
    },
    "scenarios": {
        "required": ["task", "domain", "uncertainty_mode"],
        "conditional": {
            "decision_mode": "Use this only if scenario branches need explicit action implications.",
            "evidence_mode": "Use this only if the scenario set should stay close to what can be evidenced.",
            "output_mode": "Use this only if the deliverable needs scenario-tree or dashboard-style branch emphasis.",
        },
    },
    "question_generation": {
        "required": [
            "task",
            "domain",
            "output_mode",
            "evidence_mode",
            "uncertainty_mode",
            "decision_mode",
        ],
        "conditional": {},
    },
    "evidence_planning": {
        "required": ["evidence_mode", "uncertainty_mode"],
        "conditional": {
            "task": "Use this only if the task changes what counts as enough proof.",
            "domain": "Use this only if domain-specific proof norms should change source choice.",
            "decision_mode": "Use this only if evidence timing or sufficiency depends on staged commitment, one-shot risk, or portfolio logic.",
        },
    },
    "decision_logic": {
        "required": ["decision_mode", "uncertainty_mode"],
        "conditional": {
            "task": "Use this only if the task framing materially changes the action bar.",
            "evidence_mode": "Use this only if the preferred proof style should change commitment thresholds.",
            "domain": "Use this only if domain-specific action logic should shape timing, sizing, or hedging.",
        },
    },
    "signal_translation": {
        "required": ["evidence_mode", "uncertainty_mode"],
        "conditional": {
            "decision_mode": "Use this only if the signals should change action, timing, sizing, or stage gates rather than only belief.",
            "task": "Use this only if the task changes what makes a signal decision-useful.",
            "domain": "Use this only if domain-specific signal behavior should change what is monitored.",
            "output_mode": "Use this only if the eventual deliverable shape changes signal emphasis.",
        },
    },
    "monitoring": {
        "required": ["task", "uncertainty_mode"],
        "conditional": {
            "decision_mode": "Use this only if monitoring should trigger adds, trims, stops, hedges, or scale changes.",
            "evidence_mode": "Use this only if source quality or source lag should change cadence or escalation.",
            "output_mode": "Use this only if the deliverable shape changes how compact or operational monitoring must be.",
            "domain": "Use this only if domain-specific watch patterns change what deserves monitoring attention.",
        },
    },
    "render": {
        "required": [
            "task",
            "domain",
            "output_mode",
            "evidence_mode",
            "uncertainty_mode",
            "decision_mode",
        ],
        "conditional": {},
    },
}

GUIDANCE_NOTE = (
    "Each guidance item includes an importance label that indicates how strongly "
    "it should shape the result of this stage."
)


def build_stage_guidance(
    stage: str,
    resolved_modules: dict[str, ResolvedModule],
) -> dict[str, list[dict[str, str]]]:
    normalized_stage = normalize_stage_name(stage)
    policy = STAGE_GUIDANCE_POLICY[normalized_stage]
    required_dimensions = set(policy["required"])
    conditional_dimensions = policy["conditional"]
    guidance = {"required": [], "conditional": []}

    for dimension, module in resolved_modules.items():
        entry = _build_guidance_entry(normalized_stage, module)
        if entry is None:
            continue

        if dimension in required_dimensions:
            guidance["required"].append(entry)
            continue

        condition = conditional_dimensions.get(dimension)
        if condition:
            guidance["conditional"].append({**entry, "condition": condition})

    return guidance


def render_adapter_sections(stage: str, resolved_modules: dict[str, ResolvedModule]) -> str:
    normalized_stage = normalize_stage_name(stage)
    if not resolved_modules:
        return ""

    if normalized_stage == "render":
        return _render_render_stage_guidance(resolved_modules)

    guidance = build_stage_guidance(stage, resolved_modules)
    lines = ["## Stage Guidance", GUIDANCE_NOTE]
    lines.extend(_render_guidance_entries(guidance["required"]))
    lines.extend(_render_conditional_guidance_entries(guidance["conditional"]))
    return "\n".join(lines).strip()


def _build_guidance_entry(stage: str, module: ResolvedModule) -> dict[str, str] | None:
    if module.dimension == "output_mode":
        if stage == "render":
            return None
        return {
            "dimension": module.dimension,
            "wrapper": WRAPPER_TEMPLATES[module.dimension].format(value=module.value),
            "importance": "Moderate",
            "guidance": (
                f"Keep this stage consistent with the eventual `{module.value}` deliverable. "
                "Let the deliverable shape influence emphasis and prioritization, not final section formatting."
            ),
        }

    adapter = load_adapter_payload(module.dimension, module.path)
    stage_entry = adapter.stage_guidance.get(stage)
    if stage_entry is None:
        return None

    return {
        "dimension": module.dimension,
        "wrapper": WRAPPER_TEMPLATES[module.dimension].format(value=module.value),
        "importance": stage_entry.importance,
        "guidance": stage_entry.guidance,
    }


def _render_guidance_entries(entries: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        lines.append(f"- {entry['importance']}: {entry['guidance']}")
    return lines


def _render_conditional_guidance_entries(entries: list[dict[str, str]]) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        lines.append(f'[CONDITIONAL condition="{entry["condition"]}"]')
        lines.append(f"- {entry['importance']}: {entry['guidance']}")
        lines.append("[/CONDITIONAL]")
    return lines


def _render_render_stage_guidance(resolved_modules: dict[str, ResolvedModule]) -> str:
    lines = ["## Stage Guidance", GUIDANCE_NOTE]
    for module in resolved_modules.values():
        if module.dimension == "output_mode":
            lines.append(module.path.read_text().strip())
            continue

        entry = _build_guidance_entry("render", module)
        if entry is None:
            continue
        lines.append(f"- {entry['importance']}: {entry['guidance']}")
    return "\n".join(lines).strip()
