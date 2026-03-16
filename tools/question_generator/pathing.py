from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_ROOT = REPO_ROOT / "prompt" / "question-generator"

STAGE_NAME_MAP = {
    "routing": "01-routing",
    "boundary": "02-boundary",
    "structure": "03-structure",
    "scenarios": "04-scenarios",
    "question_generation": "05-question-generation",
    "evidence_planning": "06-evidence-planning",
    "decision_logic": "07-decision-logic",
    "signal_translation": "08-signal-translation",
    "monitoring": "09-monitoring",
    "render": "10-render",
}

ADAPTER_DIR_MAP = {
    "task": "tasks",
    "domain": "domains",
    "evidence_mode": "evidence-modes",
    "uncertainty_mode": "uncertainty-modes",
    "decision_mode": "decision-modes",
}

RENDER_TEMPLATE_MAP = {
    "Research Memo": "research-memo.md",
    "Decision Memo": "decision-memo.md",
    "Monitoring Dashboard": "monitoring-dashboard.md",
    "Scenario Tree": "scenario-tree.md",
    "Deep-Research Prompt": "deep-research-prompt.md",
    "Investment Worksheet": "investment-worksheet.md",
}


def repo_root() -> Path:
    return REPO_ROOT


def contracts_dir() -> Path:
    return PROMPT_ROOT / "contracts"


def stages_dir() -> Path:
    return PROMPT_ROOT / "stages"


def adapters_dir() -> Path:
    return PROMPT_ROOT / "adapters"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def normalize_stage_name(stage: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", stage.strip().lower()).strip("_")
    return normalized


def stage_stub(stage: str) -> str:
    return STAGE_NAME_MAP[normalize_stage_name(stage)]


def contract_path(stage: str) -> Path:
    normalized_stage = normalize_stage_name(stage)
    filename = f"{stage_stub(normalized_stage)}.contract.json"
    return contracts_dir() / filename


def stage_template_path(stage: str) -> Path:
    return stages_dir() / f"{stage_stub(stage)}.md"


def adapter_family_dir(adapter_dimension: str) -> Path:
    return adapters_dir() / ADAPTER_DIR_MAP[adapter_dimension]


def adapter_path(adapter_dimension: str, routed_value: str) -> Path:
    return adapter_family_dir(adapter_dimension) / f"{_slugify(routed_value)}.json"


def render_template_path(output_mode: str) -> Path:
    try:
        filename = RENDER_TEMPLATE_MAP[output_mode]
    except KeyError as exc:
        supported = ", ".join(sorted(RENDER_TEMPLATE_MAP))
        raise ValueError(
            f"Unsupported render output mode: {output_mode!r}. Supported modes: {supported}"
        ) from exc

    return stages_dir() / "render" / filename
