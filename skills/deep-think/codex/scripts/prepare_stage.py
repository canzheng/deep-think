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


if __name__ == "__main__":
    raise SystemExit(main(["prepare-stage", *sys.argv[1:]]))
