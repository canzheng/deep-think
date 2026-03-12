from __future__ import annotations

from .common import append_named_list, legacy_section_heading


def render_evidence_plan(payload: dict[str, object]) -> list[str]:
    lines = [legacy_section_heading("evidence_plan")]
    append_named_list(lines, "Evidence hierarchy", payload.get("evidence_hierarchy"))
    append_named_list(lines, "Preferred source types", payload.get("preferred_source_types"))
    append_named_list(lines, "Backup source types", payload.get("backup_source_types"))
    append_named_list(lines, "Conflict-resolution rules", payload.get("conflict_resolution_rules"))

    mappings = payload.get("question_to_evidence_mapping")
    if isinstance(mappings, list) and mappings:
        lines.append("- Question-to-evidence mapping:")
        for item in mappings:
            if not isinstance(item, dict):
                continue
            question = item.get("question", "Question")
            lines.append(f"  - {question}")
            preferred = item.get("preferred_sources")
            if isinstance(preferred, list) and preferred:
                lines.append("    Preferred sources:")
                for source in preferred:
                    lines.append(f"      - {source}")
            backup = item.get("backup_sources")
            if isinstance(backup, list) and backup:
                lines.append("    Backup sources:")
                for source in backup:
                    lines.append(f"      - {source}")

    return lines
