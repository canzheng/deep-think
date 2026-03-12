import json
import random
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


from tools.question_generator.assembler import assemble_stage_prompt


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
POPULATED_STATE_PATH = FIXTURES_DIR / "populated_state.json"


STATE = {
    "topic": "Should we add to NVDA ahead of earnings?",
    "routing": {
        "task": "Decide",
        "domain": "Investing / Markets",
        "output_mode": "Decision Memo",
        "evidence_mode": "Market-Tape / Price-Action-First",
        "uncertainty_mode": "Hidden-Variable Dominated",
        "decision_mode": "Portfolio Construction",
    },
    "boundary": {"core_system": "NVIDIA earnings setup"},
    "structure": {"bottlenecks": ["datacenter demand durability"]},
    "scenarios": {"base_case": {"summary": "base"}},
    "questions": {"top_killer_questions": [{"question": "Is demand pull-forward?"}]},
    "evidence_plan": {"evidence_hierarchy": ["guidance", "revisions"]},
    "uncertainty_map": {"irreducible_uncertainties": ["management tone"]},
    "decision_logic": {"must_know_before_action": ["position sizing"]},
    "synthesis": {"recommendation_or_action_frame": "small add"},
    "signals": [{"signal": "estimate revisions"}],
    "monitoring": {"what_to_watch": [{"item": "estimate revisions"}]},
}


def load_populated_state() -> dict:
    with POPULATED_STATE_PATH.open() as fixture_file:
        return json.load(fixture_file)


def random_topic() -> str:
    generator = random.Random(20260312)
    token = generator.randrange(10_000, 99_999)
    return "\n".join(
        [
            f"Random topic {token}: should Atlas expand into healthcare now?",
            "```yaml",
            "risk: medium",
            "mode: staged",
            "```",
            "# keep prompt well formed",
        ]
    )


class AssemblerTest(unittest.TestCase):
    def test_question_generation_prompt_interpolates_placeholders(self) -> None:
        state = dict(STATE)
        state["topic"] = random_topic()
        with TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "question-generation.md"
            template_path.write_text(
                "\n".join(
                    [
                        "Intro",
                        "",
                        "{{topic}}",
                        "",
                        "{{current_state}}",
                        "",
                        "{{active_steering}}",
                        "",
                        "{{required_output}}",
                        "",
                        "{{feedback}}",
                    ]
                ),
                encoding="utf-8",
            )

            with patch(
                "tools.question_generator.assembler.stage_template_path",
                return_value=template_path,
            ):
                prompt = assemble_stage_prompt(
                    "question_generation",
                    state,
                    optional_reads=["boundary"],
                )

        self.assertIn("Intro", prompt)
        self.assertIn(state["topic"], prompt)
        self.assertIn("## Relevant Context", prompt)
        self.assertNotIn("## Current State", prompt)
        self.assertIn("## Stage Guidance", prompt)
        self.assertNotIn("## Active Steering", prompt)
        self.assertIn("## Required Output", prompt)
        self.assertIn("## Feedback", prompt)
        self.assertEqual(prompt.count("## Relevant Context"), 1)
        self.assertEqual(prompt.count("## Stage Guidance"), 1)
        self.assertEqual(prompt.count("## Required Output"), 1)
        self.assertEqual(prompt.count("## Feedback"), 1)
        self.assertNotIn("{{topic}}", prompt)
        self.assertNotIn("{{current_state}}", prompt)
        self.assertNotIn("{{active_steering}}", prompt)
        self.assertNotIn("{{required_output}}", prompt)
        self.assertNotIn("{{feedback}}", prompt)

    def test_question_generation_prompt_appends_blocks_without_placeholders(self) -> None:
        with TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "question-generation.md"
            template_path.write_text("Intro", encoding="utf-8")

            with patch(
                "tools.question_generator.assembler.stage_template_path",
                return_value=template_path,
            ):
                prompt = assemble_stage_prompt(
                    "question_generation",
                    STATE,
                    optional_reads=["boundary"],
                )

        self.assertTrue(prompt.startswith("Intro\n\n## Relevant Context"))
        self.assertIn("\n\n## Stage Guidance\n", prompt)
        self.assertIn("\n\n## Required Output\n", prompt)
        self.assertTrue(prompt.rstrip().endswith("```"))
        self.assertLess(prompt.index("## Relevant Context"), prompt.index("## Stage Guidance"))
        self.assertLess(prompt.index("## Stage Guidance"), prompt.index("## Required Output"))
        self.assertLess(prompt.index("## Required Output"), prompt.index("## Feedback"))

    def test_question_generation_prompt_contains_all_core_sections(self) -> None:
        prompt = assemble_stage_prompt(
            "question_generation",
            STATE,
            optional_reads=["boundary"],
        )

        self.assertIn("You are generating the question set for the current topic.", prompt)
        self.assertIn("## Relevant Context", prompt)
        self.assertNotIn("## Current State", prompt)
        self.assertIn("## Stage Guidance", prompt)
        self.assertNotIn("## Active Steering", prompt)
        self.assertIn("## Required Output", prompt)
        self.assertIn("## Feedback", prompt)
        self.assertIn("Because this is a `Decide` task", prompt)
        self.assertIn('"required": [', prompt)

    def test_real_stage_templates_assemble_cleanly_with_populated_state(self) -> None:
        state = load_populated_state()
        state["topic"] = random_topic()
        optional_reads = ["boundary", "structure", "question_generation"]
        all_stages = [
            "routing",
            "boundary",
            "structure",
            "scenarios",
            "question_generation",
            "evidence_planning",
            "decision_logic",
            "signal_translation",
            "monitoring",
            "render",
        ]

        for stage in all_stages:
            with self.subTest(stage=stage):
                prompt = assemble_stage_prompt(
                    stage,
                    state,
                    optional_reads=optional_reads,
                )

                self.assertNotIn("{{topic}}", prompt)
                self.assertNotIn("{{current_state}}", prompt)
                self.assertNotIn("{{active_steering}}", prompt)
                self.assertNotIn("{{required_output}}", prompt)
                self.assertNotIn("{{feedback}}", prompt)
                self.assertTrue(prompt.splitlines()[0].strip())
                self.assertIn(state["topic"], prompt)
                self.assertEqual(prompt.count("## Required Output"), 1)

                expected_context_count = 0 if stage == "routing" else 1
                self.assertEqual(prompt.count("## Relevant Context"), expected_context_count)
                self.assertEqual(prompt.count("## Current State"), 0)

                expected_guidance_count = 0 if stage == "routing" else 1
                self.assertEqual(prompt.count("## Stage Guidance"), expected_guidance_count)
                self.assertEqual(prompt.count("## Active Steering"), 0)

                expected_feedback_count = 1 if stage in {"question_generation", "evidence_planning"} else 0
                self.assertEqual(prompt.count("## Feedback"), expected_feedback_count)

                if "## Relevant Context" in prompt and "## Stage Guidance" in prompt:
                    self.assertLess(prompt.index("## Relevant Context"), prompt.index("## Stage Guidance"))
                if "## Stage Guidance" in prompt:
                    self.assertLess(prompt.index("## Stage Guidance"), prompt.index("## Required Output"))
                elif "## Relevant Context" in prompt:
                    self.assertLess(prompt.index("## Relevant Context"), prompt.index("## Required Output"))
                if stage == "routing":
                    self.assertLess(prompt.index("## Step 1 - Determine Primary Task"), prompt.index("## Required Output"))

                if stage != "render":
                    self.assertNotIn("Required sections:", prompt)

    def test_render_prompt_uses_full_state_and_no_feedback(self) -> None:
        prompt = assemble_stage_prompt("render", STATE)

        self.assertIn("## Stage 10 - Render", prompt)
        self.assertIn("### The current monitoring layer is:", prompt)
        self.assertIn("## Relevant Context", prompt)
        self.assertIn("## Stage Guidance", prompt)
        self.assertIn("the selected output-mode module defines the final deliverable structure and section order", prompt)
        self.assertNotIn("Always begin with:", prompt)
        self.assertNotIn("## Feedback", prompt)


if __name__ == "__main__":
    unittest.main()
