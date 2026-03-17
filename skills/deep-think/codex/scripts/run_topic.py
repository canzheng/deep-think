from __future__ import annotations

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BASE_DIR / "runtime"
VENDOR_ROOT = BASE_DIR / "vendor" / "chevron"

os.environ.setdefault("QUESTION_GENERATOR_RUNTIME_ROOT", str(RUNTIME_ROOT))
sys.path.insert(0, str(VENDOR_ROOT))
sys.path.insert(0, str(RUNTIME_ROOT))

from tools.question_generator.cli import main


DEFAULT_RECIPE = BASE_DIR / "runtime" / "prompt" / "question-generator" / "recipes" / "non-render.recipe.json"
DEFAULT_OUTPUT_DIR = BASE_DIR / "tmp" / "question-runs"


def _build_args() -> list[str]:
    args = sys.argv[1:]
    if "--recipe" not in args:
        args.extend(["--recipe", str(DEFAULT_RECIPE)])
    if "--output-dir" not in args:
        args.extend(["--output-dir", str(DEFAULT_OUTPUT_DIR)])
    return ["run-topic", *args]


if __name__ == "__main__":
    raise SystemExit(main(_build_args()))
