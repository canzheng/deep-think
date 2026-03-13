import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


from tools.question_generator.adapter_rendering import render_adapter_sections
from tools.question_generator.models import ResolvedModule


class AdapterRenderingTest(unittest.TestCase):
    def test_rendered_stage_guidance_uses_structured_json_and_prompt_facing_labels(self) -> None:
        adapter_payload = {
            "value": "Decide",
            "prioritize": [
                "action relevance",
                "timing",
            ],
            "stage_guidance": {
                "decision_logic": {
                    "importance": "Important",
                    "guidance": "Make action thresholds explicit.",
                }
            },
        }

        with TemporaryDirectory() as tmpdir:
            adapter_path = Path(tmpdir) / "decide.json"
            adapter_path.write_text(json.dumps(adapter_payload), encoding="utf-8")
            resolved = {
                "task": ResolvedModule(
                    dimension="task",
                    value="Decide",
                    path=adapter_path,
                )
            }

            rendered = render_adapter_sections("decision_logic", resolved)

        self.assertIn("## Stage Guidance", rendered)
        self.assertIn(
            "Each guidance item includes an importance label that indicates how strongly it should shape the result of this stage.",
            rendered,
        )
        self.assertIn("- Important: Make action thresholds explicit.", rendered)
        self.assertNotIn("Relevance:", rendered)
        self.assertNotIn("## Stage Relevance", rendered)
        self.assertNotIn("Primary", rendered)
        self.assertNotIn("Modulating", rendered)

    def test_rendered_stage_guidance_wraps_conditional_items(self) -> None:
        adapter_payload = {
            "value": "Portfolio Construction",
            "use_when": [
                "allocation across multiple opportunities matters",
            ],
            "research_behavior": [
                "evaluate portfolio role rather than standalone attractiveness",
            ],
            "key_questions": [
                "What role does this play in the portfolio?",
            ],
            "action_logic": [
                "define sizing and substitution logic",
            ],
            "monitoring_style": [
                "track both position-level and portfolio-level stress signals",
            ],
            "failure_mode": [
                "false diversification",
            ],
            "stage_guidance": {
                "decision_logic": {
                    "importance": "Important",
                    "guidance": "Define sizing, diversification, hedging, and substitution logic.",
                },
                "monitoring": {
                    "importance": "Moderate",
                    "guidance": "Include portfolio-level stress signals when overlap or correlation could change action.",
                },
            },
        }

        with TemporaryDirectory() as tmpdir:
            adapter_path = Path(tmpdir) / "portfolio-construction.json"
            adapter_path.write_text(json.dumps(adapter_payload), encoding="utf-8")
            resolved = {
                "decision_mode": ResolvedModule(
                    dimension="decision_mode",
                    value="Portfolio Construction",
                    path=adapter_path,
                )
            }

            rendered = render_adapter_sections("monitoring", resolved)

        self.assertIn(
            '[CONDITIONAL condition="Use this only if monitoring should trigger adds, trims, stops, hedges, or scale changes."]',
            rendered,
        )
        self.assertIn(
            "- Moderate: Include portfolio-level stress signals when overlap or correlation could change action.",
            rendered,
        )
        self.assertIn("[/CONDITIONAL]", rendered)


if __name__ == "__main__":
    unittest.main()
