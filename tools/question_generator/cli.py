from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.question_generator.assembler import assemble_stage_prompt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assemble a question-generator stage prompt.")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--include-optional", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    state_path = Path(args.state)
    with state_path.open() as state_file:
        state = json.load(state_file)

    prompt = assemble_stage_prompt(
        args.stage,
        state,
        optional_reads=args.include_optional,
    )
    print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
