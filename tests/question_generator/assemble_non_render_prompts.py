from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
import re
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.question_generator.assembler import assemble_stage_prompt

NON_RENDER_STAGES = [
    "routing",
    "boundary",
    "structure",
    "scenarios",
    "question_generation",
    "evidence_planning",
    "decision_logic",
    "signal_translation",
    "monitoring",
]

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
POPULATED_STATE_PATH = FIXTURES_DIR / "populated_state.json"
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parent / "artifacts" / "non_render_prompt_review_bundle.md"
)
DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parent / "artifacts" / "non_render_prompt_review_prompts"
)
DEFAULT_MANIFEST_PATH = (
    Path(__file__).resolve().parent / "artifacts" / "non_render_prompt_review_manifest.json"
)
TOPIC_POOL = [
    "Should we add to NVDA ahead of earnings if hyperscaler capex holds but China restrictions tighten?",
    "If a late-stage AI startup depends on GPU subsidies and regulatory waivers, what should management decide in the next 12 months?",
    "Which signals matter most if export controls shift while demand stays strong but supply remains politically constrained?",
]


def choose_review_topic(seed: int = 20260313) -> str:
    generator = random.Random(seed)
    return generator.choice(TOPIC_POOL)


def load_populated_state() -> dict:
    with POPULATED_STATE_PATH.open() as fixture_file:
        return json.load(fixture_file)


def _markdown_fence(text: str, language: str) -> str:
    longest_run = max(4, max((len(match) for match in re.findall(r"`+", text)), default=0) + 1)
    return f"{'`' * longest_run}{language}"


def build_review_bundle(seed: int = 20260313) -> str:
    state = load_populated_state()
    topic = choose_review_topic(seed=seed)
    state["topic"] = topic

    sections = [
        "# Non-Render Prompt Review Bundle",
        "",
        "## Review Topic",
        "```text",
        topic,
        "```",
    ]

    for stage in NON_RENDER_STAGES:
        prompt = assemble_stage_prompt(stage, state)
        fence_open = _markdown_fence(prompt, "md")
        fence_close = "`" * (len(fence_open) - 2)
        sections.extend(
            [
                "",
                f"## Stage: {stage}",
                fence_open,
                prompt,
                fence_close,
            ]
        )

    return "\n".join(sections)


def build_review_prompt_set(seed: int = 20260313) -> dict:
    state = load_populated_state()
    topic = choose_review_topic(seed=seed)
    state["topic"] = topic

    prompts: dict[str, str] = {}
    for stage in NON_RENDER_STAGES:
        prompts[stage] = assemble_stage_prompt(stage, state)

    return {
        "seed": seed,
        "topic": topic,
        "prompts": prompts,
    }


def write_review_prompt_set(output_dir: Path, manifest_path: Path, seed: int = 20260313) -> dict:
    prompt_set = build_review_prompt_set(seed=seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    prompt_entries = []
    for stage, prompt in prompt_set["prompts"].items():
        prompt_path = output_dir / f"{stage}.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        prompt_entries.append(
            {
                "stage": stage,
                "path": str(prompt_path),
            }
        )

    manifest = {
        "seed": prompt_set["seed"],
        "topic": prompt_set["topic"],
        "prompts": prompt_entries,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Assemble all non-render stage prompts into separate review files."
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--seed", type=int, default=20260313)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    write_review_prompt_set(
        output_dir=Path(args.output_dir),
        manifest_path=Path(args.manifest),
        seed=args.seed,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
