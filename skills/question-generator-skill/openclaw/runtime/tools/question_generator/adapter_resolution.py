from __future__ import annotations

from tools.question_generator.models import ResolvedModule, StageContract
from tools.question_generator.pathing import adapter_path, normalize_stage_name, render_template_path


def resolve_stage_modules(
    contract: StageContract,
    routing: dict[str, str],
) -> dict[str, ResolvedModule]:
    if normalize_stage_name(contract.stage) == "routing":
        return {}

    resolved: dict[str, ResolvedModule] = {}
    for dimension in contract.depends_on:
        value = routing.get(dimension)
        if not value:
            raise ValueError(f"Missing routed value for dependency '{dimension}'")

        if dimension == "output_mode":
            path = render_template_path(value)
        else:
            path = adapter_path(dimension, value)

        resolved[dimension] = ResolvedModule(
            dimension=dimension,
            value=value,
            path=path,
        )

    return resolved
