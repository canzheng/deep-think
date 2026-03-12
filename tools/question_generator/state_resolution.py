from __future__ import annotations

from collections import OrderedDict

from tools.question_generator.models import StageContract
from tools.question_generator.pathing import normalize_stage_name


STAGE_TO_STATE_SECTIONS = {
    "topic": ["topic"],
    "routing": ["routing"],
    "boundary": ["boundary"],
    "structure": ["structure"],
    "scenarios": ["scenarios"],
    "question_generation": ["questions"],
    "evidence_planning": ["evidence_plan", "uncertainty_map"],
    "decision_logic": ["decision_logic", "synthesis"],
    "signal_translation": ["signals"],
    "monitoring": ["monitoring"],
}


def resolve_state_sections(
    contract: StageContract,
    state: dict,
    optional_reads: list[str] | None = None,
) -> OrderedDict[str, object]:
    if normalize_stage_name(contract.stage) == "render":
        return OrderedDict(state.items())

    sections: OrderedDict[str, object] = OrderedDict()
    for read in contract.reads_required or []:
        _add_read_sections(sections, read, state)

    selected_optionals = {
        normalize_stage_name(stage_name)
        for stage_name in (optional_reads or [])
    }
    for optional in contract.reads_optional or []:
        if normalize_stage_name(optional.stage) in selected_optionals:
            _add_read_sections(sections, optional.stage, state)

    return sections


def _add_read_sections(sections: OrderedDict[str, object], read: str, state: dict) -> None:
    normalized_read = normalize_stage_name(read)
    for state_section in STAGE_TO_STATE_SECTIONS[normalized_read]:
        sections[state_section] = state[state_section]
