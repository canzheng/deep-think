from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from tools.question_generator.assembler import assemble_stage_prompt
from tools.question_generator.orchestrator import (
    apply_stage_response,
    initialize_topic_run,
    initialize_run,
    load_recipe,
    prepare_stage,
    run_recipe,
    run_recipe_on_run,
    run_stage,
    run_topic,
    update_routing,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assemble a question-generator stage prompt.")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--include-optional", action="append", default=[])
    return parser


def build_workflow_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run question-generator orchestration tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-run")
    init_parser.add_argument("--state", required=True)
    init_parser.add_argument("--output-dir", required=True)
    init_parser.add_argument("--run-id", required=True)

    init_topic_parser = subparsers.add_parser("init-topic-run")
    init_topic_parser.add_argument("--topic", required=True)
    init_topic_parser.add_argument("--output-dir", required=True)
    init_topic_parser.add_argument("--run-id", required=True)

    prepare_parser = subparsers.add_parser("prepare-stage")
    prepare_parser.add_argument("--run-dir", required=True)
    prepare_parser.add_argument("--stage", required=True)
    prepare_parser.add_argument("--include-optional", action="append", default=[])

    apply_parser = subparsers.add_parser("apply-response")
    apply_parser.add_argument("--run-dir", required=True)
    apply_parser.add_argument("--stage", required=True)
    apply_parser.add_argument("--response", required=True)

    run_parser = subparsers.add_parser("run-stage")
    run_parser.add_argument("--run-dir", required=True)
    run_parser.add_argument("--stage", required=True)
    run_parser.add_argument("--include-optional", action="append", default=[])
    run_parser.add_argument("--codex-bin", default="codex")
    run_parser.add_argument("--timeout-seconds", type=int, default=120)

    recipe_parser = subparsers.add_parser("run-recipe")
    recipe_parser.add_argument("--recipe", required=True)
    recipe_parser.add_argument("--state", required=True)
    recipe_parser.add_argument("--output-dir", required=True)
    recipe_parser.add_argument("--run-id", required=True)
    recipe_parser.add_argument("--codex-bin", default="codex")
    recipe_parser.add_argument("--timeout-seconds", type=int, default=120)

    recipe_on_run_parser = subparsers.add_parser("run-recipe-on-run")
    recipe_on_run_parser.add_argument("--recipe", required=True)
    recipe_on_run_parser.add_argument("--run-dir", required=True)
    recipe_on_run_parser.add_argument("--start-stage")
    recipe_on_run_parser.add_argument("--stop-stage")
    recipe_on_run_parser.add_argument("--codex-bin", default="codex")
    recipe_on_run_parser.add_argument("--timeout-seconds", type=int, default=120)

    update_routing_parser = subparsers.add_parser("update-routing")
    update_routing_parser.add_argument("--run-dir", required=True)
    update_routing_parser.add_argument("--patch-json", required=True)

    run_topic_parser = subparsers.add_parser("run-topic")
    run_topic_parser.add_argument("--topic", required=True)
    run_topic_parser.add_argument("--recipe", required=True)
    run_topic_parser.add_argument("--output-dir", required=True)
    run_topic_parser.add_argument("--run-id", required=True)
    run_topic_parser.add_argument("--pause-after-stage")
    run_topic_parser.add_argument("--codex-bin", default="codex")
    run_topic_parser.add_argument("--timeout-seconds", type=int, default=120)

    return parser


def main(argv: list[str] | None = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if not args_list or args_list[0].startswith("-"):
        args = build_parser().parse_args(args_list)
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

    args = build_workflow_parser().parse_args(args_list)
    if args.command == "init-run":
        run_dir = initialize_run(
            state_path=Path(args.state),
            output_dir=Path(args.output_dir),
            run_id=args.run_id,
        )
        print(run_dir)
        return 0

    if args.command == "init-topic-run":
        run_dir = initialize_topic_run(
            topic=args.topic,
            output_dir=Path(args.output_dir),
            run_id=args.run_id,
        )
        print(run_dir)
        return 0

    if args.command == "prepare-stage":
        record = prepare_stage(
            Path(args.run_dir),
            args.stage,
            optional_reads=args.include_optional,
        )
        print(record["prompt_path"])
        return 0

    if args.command == "apply-response":
        record = apply_stage_response(
            Path(args.run_dir),
            args.stage,
            response_path=Path(args.response),
        )
        print(record.get("response_parsed_path") or record.get("response_raw_path"))
        return 0

    if args.command == "run-stage":
        record = run_stage(
            Path(args.run_dir),
            args.stage,
            optional_reads=args.include_optional,
            codex_bin=args.codex_bin,
            timeout_seconds=args.timeout_seconds,
        )
        print(record.get("response_parsed_path") or record.get("response_raw_path"))
        return 0

    if args.command == "run-recipe":
        result = run_recipe(
            recipe_path=Path(args.recipe),
            state_path=Path(args.state),
            output_dir=Path(args.output_dir),
            run_id=args.run_id,
            codex_bin=args.codex_bin,
            timeout_seconds=args.timeout_seconds,
        )
        print(result["run_dir"])
        return 0

    if args.command == "run-recipe-on-run":
        result = run_recipe_on_run(
            recipe_path=Path(args.recipe),
            run_dir=Path(args.run_dir),
            start_stage=args.start_stage,
            stop_stage=args.stop_stage,
            codex_bin=args.codex_bin,
            timeout_seconds=args.timeout_seconds,
        )
        print(result["run_dir"])
        return 0

    if args.command == "update-routing":
        patch = json.loads(args.patch_json)
        updated = update_routing(
            Path(args.run_dir),
            patch,
        )
        print(json.dumps(updated, indent=2, ensure_ascii=True))
        return 0

    if args.command == "run-topic":
        result = run_topic(
            topic=args.topic,
            recipe_path=Path(args.recipe),
            output_dir=Path(args.output_dir),
            run_id=args.run_id,
            pause_after_stage=args.pause_after_stage,
            codex_bin=args.codex_bin,
            timeout_seconds=args.timeout_seconds,
        )
        print(result["run_dir"])
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
