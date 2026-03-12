from __future__ import annotations

from tools.question_generator.renderers import render_section


def render_state_sections(stage: str, sections: dict[str, object]) -> str:
    rendered_sections = ["## Relevant Context"]
    for section_name, payload in sections.items():
        rendered_sections.extend(render_section(section_name, payload))

    return "\n".join(rendered_sections)
