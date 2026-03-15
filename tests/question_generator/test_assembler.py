import json
import random
import unittest
from types import SimpleNamespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


from tools.question_generator.assembler import assemble_stage_prompt
from tools.question_generator.adapter_rendering import build_stage_guidance
from tools.question_generator.adapter_resolution import resolve_stage_modules
from tools.question_generator.contracts import load_contract
from tools.question_generator.render_context import build_render_context, render_wrapper_template


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
    def _render_prompt_for_mode(self, output_mode: str) -> str:
        state = load_populated_state()
        state["routing"]["output_mode"] = output_mode
        return assemble_stage_prompt("render", state)

    def _render_guidance_for_mode(self, output_mode: str) -> dict:
        state = load_populated_state()
        state["routing"]["output_mode"] = output_mode
        contract = load_contract("render")
        resolved_modules = resolve_stage_modules(contract, state["routing"])
        stage_guidance = build_stage_guidance("render", resolved_modules)
        context = build_render_context(
            state,
            stage_guidance=stage_guidance,
            required_output_schema="",
            feedback_schema="",
        )
        return context["stage_guidance"]

    def test_decision_logic_prompt_supports_mustache_sections_for_repeated_objects(self) -> None:
        state = load_populated_state()
        with TemporaryDirectory() as tmpdir:
            template_path = Path(tmpdir) / "decision-logic.md"
            template_path.write_text(
                "\n".join(
                    [
                        "Alternatives:",
                        "{{#scenarios.alternative_scenarios}}",
                        "### {{name}}",
                        "Summary: {{summary}}",
                        "{{#branch_points}}",
                        "- {{.}}",
                        "{{/branch_points}}",
                        "{{/scenarios.alternative_scenarios}}",
                        "",
                        "{{required_output_schema}}",
                    ]
                ),
                encoding="utf-8",
            )

            with patch(
                "tools.question_generator.assembler.stage_template_path",
                return_value=template_path,
            ):
                prompt = assemble_stage_prompt("decision_logic", state)

        self.assertIn("Compliance drag stalls rollout", prompt)
        self.assertIn("Weak workflow fit", prompt)
        self.assertNotIn("{{#scenarios.alternative_scenarios}}", prompt)
        self.assertNotIn("{{name}}", prompt)
        self.assertNotIn("{{.}}", prompt)

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
                        "{{{topic}}}",
                        "",
                        "Time horizon: {{routing.time_horizon}}",
                        "",
                        "## Stage Guidance",
                        "Each guidance item includes an importance label that indicates how strongly it should shape the result of this stage.",
                        "{{#stage_guidance.required}}",
                        "- {{importance}}: {{guidance}}",
                        "{{/stage_guidance.required}}",
                        "{{#stage_guidance.conditional}}",
                        "[CONDITIONAL condition=\"{{condition}}\"]",
                        "- {{importance}}: {{guidance}}",
                        "[/CONDITIONAL]",
                        "{{/stage_guidance.conditional}}",
                        "",
                        "## Required Output",
                        "{{{required_output_schema}}}",
                        "",
                        "{{#feedback_schema}}",
                        "## Feedback",
                        "{{{feedback_schema}}}",
                        "{{/feedback_schema}}",
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
        self.assertIn("Time horizon:", prompt)
        self.assertNotIn("## Relevant Context", prompt)
        self.assertIn("## Stage Guidance", prompt)
        self.assertIn(
            "Each guidance item includes an importance label that indicates how strongly it should shape the result of this stage.",
            prompt,
        )
        self.assertIn("- Important:", prompt)
        self.assertIn("## Required Output", prompt)
        self.assertIn("## Feedback", prompt)
        self.assertEqual(prompt.count("## Stage Guidance"), 1)
        self.assertEqual(prompt.count("## Required Output"), 1)
        self.assertEqual(prompt.count("## Feedback"), 1)
        self.assertNotIn("{{topic}}", prompt)
        self.assertNotIn("{{stage_guidance}}", prompt)
        self.assertNotIn("{{required_output_schema}}", prompt)
        self.assertNotIn("{{feedback_schema}}", prompt)

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

        self.assertEqual(prompt, "Intro")

    def test_question_generation_prompt_contains_all_core_sections(self) -> None:
        prompt = assemble_stage_prompt(
            "question_generation",
            STATE,
            optional_reads=["boundary"],
        )

        self.assertIn("You are generating the question set for the current topic.", prompt)
        self.assertIn("Scope anchors:", prompt)
        self.assertNotIn("## Relevant Context", prompt)
        self.assertIn("## Stage Guidance", prompt)
        self.assertIn("## Required Output", prompt)
        self.assertIn("## Feedback", prompt)
        self.assertIn('"required": [', prompt)

    def test_decision_logic_prompt_expands_required_output_schema_refs(self) -> None:
        prompt = assemble_stage_prompt("decision_logic", load_populated_state())

        self.assertIn("## Required Output", prompt)
        self.assertNotIn('"$ref"', prompt)
        self.assertIn('"must_know_before_action"', prompt)
        self.assertIn('"recommendation_or_action_frame"', prompt)

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
                self.assertNotIn("{{{required_output_schema}}}", prompt)
                self.assertTrue(prompt.splitlines()[0].strip())
                self.assertIn(state["topic"], prompt)
                expected_required_output_count = 0 if stage == "render" else 1
                self.assertEqual(prompt.count("## Required Output"), expected_required_output_count)
                self.assertEqual(
                    prompt.count("[CONDITIONAL condition="),
                    prompt.count("[/CONDITIONAL]"),
                )

                if stage != "render":
                    self.assertNotIn("## Relevant Context", prompt)
                    self.assertNotIn("## Current State", prompt)
                    expected_guidance_count = 0 if stage == "routing" else 1
                    self.assertEqual(prompt.count("## Stage Guidance"), expected_guidance_count)

                if stage in {
                    "boundary",
                    "structure",
                    "scenarios",
                    "question_generation",
                    "evidence_planning",
                    "decision_logic",
                    "signal_translation",
                    "monitoring",
                }:
                    self.assertNotIn("Task: Decide", prompt)
                    self.assertNotIn("Domain: Investing / Markets", prompt)
                    self.assertNotIn("Output mode: Decision Memo", prompt)
                    self.assertNotIn("Evidence mode: Market-Tape / Price-Action-First", prompt)
                    self.assertNotIn("Uncertainty mode: Hidden-Variable Dominated", prompt)
                    self.assertNotIn("Decision mode: Portfolio Construction", prompt)

                expected_feedback_count = 1 if stage in {"question_generation", "evidence_planning"} else 0
                self.assertEqual(prompt.count("## Feedback"), expected_feedback_count)

                if "## Stage Guidance" in prompt and "## Required Output" in prompt:
                    self.assertLess(prompt.index("## Stage Guidance"), prompt.index("## Required Output"))
                if stage == "routing":
                    self.assertLess(prompt.index("## Step 1 - Determine Primary Task"), prompt.index("## Required Output"))

                if stage != "render":
                    self.assertNotIn("Required sections:", prompt)

    def test_render_prompt_uses_full_state_and_no_feedback(self) -> None:
        prompt = assemble_stage_prompt("render", STATE)

        self.assertIn("You are generating the final deliverable for the current topic.", prompt)
        self.assertNotIn("## Relevant Context", prompt)
        self.assertNotIn("### The current routing for this run is:", prompt)
        self.assertNotIn("{{current_state}}", prompt)
        self.assertNotIn("{{active_steering}}", prompt)
        self.assertNotIn("## Feedback", prompt)

    def test_render_selects_mode_specific_templates(self) -> None:
        from tools.question_generator.render_context import select_render_template

        decision_template = select_render_template("Decision Memo")
        monitoring_template = select_render_template("Monitoring Dashboard")
        scenario_tree_template = select_render_template("Scenario Tree")

        self.assertNotEqual(decision_template, monitoring_template)
        self.assertNotEqual(decision_template, scenario_tree_template)
        self.assertTrue(str(decision_template).endswith("stages/render/decision-memo.md"))
        self.assertTrue(str(monitoring_template).endswith("stages/render/monitoring-dashboard.md"))
        self.assertTrue(str(scenario_tree_template).endswith("stages/render/scenario-tree.md"))

    def test_render_wrapper_no_longer_owns_stage_guidance(self) -> None:
        wrapper = render_wrapper_template().read_text(encoding="utf-8")

        self.assertNotIn("## Stage Guidance", wrapper)
        self.assertNotIn("stage guidance", wrapper.lower())

    def test_decision_memo_render_filters_stage_guidance_to_decision_and_uncertainty(self) -> None:
        guidance = self._render_guidance_for_mode("Decision Memo")

        self.assertEqual(
            {entry["dimension"] for entry in guidance["required"]},
            {"decision_mode", "uncertainty_mode"},
        )
        self.assertEqual(
            {entry["dimension"] for entry in guidance["conditional"]},
            {"evidence_mode"},
        )

    def test_research_memo_render_filters_stage_guidance_to_memo_relevant_dimensions(self) -> None:
        guidance = self._render_guidance_for_mode("Research Memo")

        self.assertEqual(
            {entry["dimension"] for entry in guidance["required"]},
            {"domain", "evidence_mode", "uncertainty_mode"},
        )
        self.assertEqual(
            {entry["dimension"] for entry in guidance["conditional"]},
            {"decision_mode"},
        )

    def test_deep_research_render_filters_stage_guidance_to_research_relevant_dimensions(self) -> None:
        guidance = self._render_guidance_for_mode("Deep-Research Prompt")

        self.assertEqual(
            {entry["dimension"] for entry in guidance["required"]},
            {"evidence_mode", "uncertainty_mode", "decision_mode"},
        )
        self.assertEqual(
            {entry["dimension"] for entry in guidance["conditional"]},
            {"domain"},
        )

    def test_decision_memo_render_prompt_uses_filtered_stage_guidance(self) -> None:
        prompt = self._render_prompt_for_mode("Decision Memo")

        self.assertIn(
            "- Moderate: Outputs should make staged commitment and option value explicit.",
            prompt,
        )
        self.assertIn(
            "- Moderate: Should show uncertainty explicitly and distinguish evidence from inference.",
            prompt,
        )
        self.assertIn(
            '[CONDITIONAL condition="Use this only if the preferred proof style should change how high the evidence bar is presented."]',
            prompt,
        )
        self.assertNotIn(
            "- Important: Pushes the final artifact toward recommendation, evidence threshold, and triggers.",
            prompt,
        )
        self.assertNotIn(
            "- Light: Mainly affects examples and operational vocabulary.",
            prompt,
        )

    def test_research_memo_render_includes_uncertainty_map_and_research_priorities(self) -> None:
        prompt = self._render_prompt_for_mode("Research Memo")

        self.assertIn("Uncertainty map:", prompt)
        self.assertIn(
            "whether pilot success will be strong and repeatable enough to justify expansion",
            prompt,
        )
        self.assertIn("Research priorities:", prompt)

    def test_monitoring_dashboard_render_includes_dominant_modes(self) -> None:
        prompt = self._render_prompt_for_mode("Monitoring Dashboard")

        self.assertIn("Dominant uncertainty mode:", prompt)
        self.assertIn("Dominant decision mode:", prompt)
        self.assertIn("Hidden-Variable Dominated", prompt)
        self.assertIn("Optionality / Staged Commitment", prompt)

    def test_scenario_tree_render_includes_evidence_shift_section(self) -> None:
        prompt = self._render_prompt_for_mode("Scenario Tree")

        self.assertIn("Evidence and signals that would shift scenario confidence:", prompt)
        self.assertIn("What would change the conclusion:", prompt)

    def test_deep_research_render_includes_mode_labels_and_rule_inputs(self) -> None:
        prompt = self._render_prompt_for_mode("Deep-Research Prompt")

        self.assertIn("Evidence mode and source priorities:", prompt)
        self.assertIn("Evidence mode: Operating-Metric-First", prompt)
        self.assertIn("Uncertainty mode: Hidden-Variable Dominated", prompt)
        self.assertIn("Decision mode: Optionality / Staged Commitment", prompt)
        self.assertIn("Treat single-customer anecdotes as weak unless supported by metrics", prompt)
        self.assertIn("Healthcare buyers care more about workflow reliability than novelty.", prompt)

    def test_render_context_uses_contract_declared_common_and_mode_reads(self) -> None:
        state = load_populated_state()
        state["routing"]["output_mode"] = "Decision Memo"
        contract = SimpleNamespace(
            reads_required_common=["topic", "routing"],
            reads_by_output_mode={
                "Decision Memo": ["decision_logic", "questions"],
            },
        )

        with patch("tools.question_generator.render_context.load_contract", return_value=contract):
            context = build_render_context(
                state,
                stage_guidance={"required": [], "conditional": []},
                required_output_schema="",
                feedback_schema="",
            )

        self.assertIn("topic", context)
        self.assertIn("routing", context)
        self.assertIn("decision_logic", context)
        self.assertIn("questions", context)
        self.assertNotIn("scenarios", context)
        self.assertNotIn("boundary", context)

    def test_investment_worksheet_render_includes_uncertainty_mode_rationale(self) -> None:
        prompt = self._render_prompt_for_mode("Investment Worksheet")

        self.assertIn("Uncertainty mode rationale:", prompt)
        self.assertIn("Hidden-Variable Dominated", prompt)

    def test_research_memo_render_includes_what_to_monitor_next(self) -> None:
        prompt = self._render_prompt_for_mode("Research Memo")

        self.assertIn("What to monitor next:", prompt)
        self.assertIn("time-to-compliance approval", prompt)

    def test_monitoring_dashboard_render_includes_compact_evidence_and_decision_implications(self) -> None:
        prompt = self._render_prompt_for_mode("Monitoring Dashboard")

        self.assertIn("Evidence plan:", prompt)
        self.assertIn("Decision-mode implications:", prompt)
        self.assertIn("What must be known before acting:", prompt)
        self.assertIn("What can be learned after acting:", prompt)
        self.assertIn("Appropriate evidence threshold:", prompt)

    def test_scenario_tree_render_includes_what_to_monitor_next(self) -> None:
        prompt = self._render_prompt_for_mode("Scenario Tree")

        self.assertIn("What to monitor next:", prompt)
        self.assertIn("implementation queue length", prompt)

    def test_deep_research_render_includes_uncertainty_map_and_conclusion_change_sections(self) -> None:
        prompt = self._render_prompt_for_mode("Deep-Research Prompt")

        self.assertIn("Uncertainty map:", prompt)
        self.assertIn("What to monitor next:", prompt)
        self.assertIn("What would change the conclusion:", prompt)

    def test_investment_worksheet_render_includes_what_to_monitor_next(self) -> None:
        prompt = self._render_prompt_for_mode("Investment Worksheet")

        self.assertIn("What to monitor next:", prompt)

    def test_monitoring_dashboard_render_includes_no_essay_quality_rule(self) -> None:
        prompt = self._render_prompt_for_mode("Monitoring Dashboard")

        self.assertIn("Do not drift into essay form.", prompt)

    def test_deep_research_render_requires_directly_executable_final_prompt(self) -> None:
        prompt = self._render_prompt_for_mode("Deep-Research Prompt")

        self.assertIn(
            "The final prompt must be directly executable and avoid extra framing that would get in the user's way.",
            prompt,
        )

    def test_render_wrapper_avoids_question_duplication_in_subtemplates(self) -> None:
        decision_prompt = self._render_prompt_for_mode("Decision Memo")
        deep_research_prompt = self._render_prompt_for_mode("Deep-Research Prompt")
        worksheet_prompt = self._render_prompt_for_mode("Investment Worksheet")

        self.assertEqual(decision_prompt.count("Decision to be made:"), 0)
        self.assertEqual(deep_research_prompt.count("Research objective:"), 0)
        self.assertEqual(worksheet_prompt.count("Expression type:"), 0)
        self.assertEqual(deep_research_prompt.count("Prefer reversible moves"), 1)
        self.assertEqual(
            deep_research_prompt.count("Healthcare buyers care more about workflow reliability than novelty."),
            1,
        )


if __name__ == "__main__":
    unittest.main()
