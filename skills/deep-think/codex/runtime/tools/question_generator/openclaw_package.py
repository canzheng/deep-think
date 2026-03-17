from __future__ import annotations

import inspect
import json
import os
import shutil
from pathlib import Path

import chevron

from tools.question_generator.openclaw_config import OPENCLAW_RUNTIME_CONFIG_PATH_ENV_VAR
from tools.question_generator.pathing import repo_root


PACKAGE_RUNTIME_ROOT_ENV_VAR = "QUESTION_GENERATOR_RUNTIME_ROOT"
PACKAGE_CONFIG_PATH_ENV_VAR = OPENCLAW_RUNTIME_CONFIG_PATH_ENV_VAR

_DEFAULT_RUNTIME_CONFIG = {
    "json_executor": "auto",
}


def default_openclaw_package_dir() -> Path:
    return repo_root() / "skills" / "deep-think" / "openclaw"


def build_openclaw_package(*, output_dir: Path | None = None) -> Path:
    package_dir = output_dir or default_openclaw_package_dir()
    package_dir.mkdir(parents=True, exist_ok=True)

    _copy_skill_markdown(package_dir)
    _write_runtime_config(package_dir)
    _write_scripts(package_dir)
    _copy_runtime_tree(package_dir)
    _copy_prompt_assets(package_dir)
    _vendor_chevron(package_dir)
    return package_dir


def _copy_skill_markdown(package_dir: Path) -> None:
    source_path = default_openclaw_package_dir() / "SKILL.md"
    destination_path = package_dir / "SKILL.md"
    if source_path.resolve() == destination_path.resolve():
        return
    shutil.copy2(source_path, destination_path)


def _write_runtime_config(package_dir: Path) -> None:
    config_dir = package_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "runtime.json").write_text(
        json.dumps(_DEFAULT_RUNTIME_CONFIG, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _write_scripts(package_dir: Path) -> None:
    scripts_dir = package_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    _write_script(scripts_dir / "run_topic.py", _run_topic_script())
    _write_script(scripts_dir / "update_routing.py", _update_routing_script())
    _write_script(scripts_dir / "resume_run.py", _resume_run_script())


def _write_script(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _copy_runtime_tree(package_dir: Path) -> None:
    source_dir = repo_root() / "tools" / "question_generator"
    destination_dir = package_dir / "runtime" / "tools" / "question_generator"
    shutil.rmtree(destination_dir, ignore_errors=True)
    destination_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, destination_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _copy_prompt_assets(package_dir: Path) -> None:
    source_dir = repo_root() / "prompt" / "question-generator"
    destination_dir = package_dir / "runtime" / "prompt" / "question-generator"
    shutil.rmtree(destination_dir, ignore_errors=True)
    destination_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, destination_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _vendor_chevron(package_dir: Path) -> None:
    vendor_root = package_dir / "vendor" / "chevron"
    chevron_package_dir = Path(inspect.getfile(chevron)).resolve().parent
    destination_dir = vendor_root / "chevron"
    shutil.rmtree(destination_dir, ignore_errors=True)
    vendor_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(chevron_package_dir, destination_dir, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def _script_prelude() -> str:
    return """from __future__ import annotations

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = BASE_DIR / "runtime"
VENDOR_ROOT = BASE_DIR / "vendor" / "chevron"
CONFIG_PATH = BASE_DIR / "config" / "runtime.json"

os.environ.setdefault("QUESTION_GENERATOR_RUNTIME_ROOT", str(RUNTIME_ROOT))
os.environ.setdefault("QUESTION_GENERATOR_OPENCLAW_CONFIG_PATH", str(CONFIG_PATH))
sys.path.insert(0, str(VENDOR_ROOT))
sys.path.insert(0, str(RUNTIME_ROOT))

from tools.question_generator.cli import main
"""


def _run_topic_script() -> str:
    return _script_prelude() + """

DEFAULT_RECIPE = BASE_DIR / "runtime" / "prompt" / "question-generator" / "recipes" / "non-render.recipe.json"
DEFAULT_OUTPUT_DIR = BASE_DIR / "tmp" / "question-runs"


def _build_args() -> list[str]:
    args = sys.argv[1:]
    if "--recipe" not in args:
        args.extend(["--recipe", str(DEFAULT_RECIPE)])
    if "--output-dir" not in args:
        args.extend(["--output-dir", str(DEFAULT_OUTPUT_DIR)])
    if "--executor-backend" not in args:
        args.extend(["--executor-backend", "openclaw"])
    return ["run-topic", *args]


if __name__ == "__main__":
    raise SystemExit(main(_build_args()))
"""


def _update_routing_script() -> str:
    return _script_prelude() + """

if __name__ == "__main__":
    raise SystemExit(main(["update-routing", *sys.argv[1:]]))
"""


def _resume_run_script() -> str:
    return _script_prelude() + """

DEFAULT_RECIPE = BASE_DIR / "runtime" / "prompt" / "question-generator" / "recipes" / "non-render.recipe.json"


def _build_args() -> list[str]:
    args = sys.argv[1:]
    if "--recipe" not in args:
        args.extend(["--recipe", str(DEFAULT_RECIPE)])
    if "--executor-backend" not in args:
        args.extend(["--executor-backend", "openclaw"])
    return ["run-recipe-on-run", *args]


if __name__ == "__main__":
    raise SystemExit(main(_build_args()))
"""


def refresh_openclaw_package(*, output_dir: Path | None = None) -> Path:
    return build_openclaw_package(output_dir=output_dir)
