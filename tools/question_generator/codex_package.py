from __future__ import annotations

import inspect
import os
import shutil
from pathlib import Path

import chevron

from tools.question_generator.pathing import PACKAGE_RUNTIME_ROOT_ENV_VAR, repo_root


def default_codex_package_dir() -> Path:
    return repo_root() / "skills" / "deep-think" / "codex"


def build_codex_package(*, output_dir: Path | None = None) -> Path:
    package_dir = output_dir or default_codex_package_dir()
    package_dir.mkdir(parents=True, exist_ok=True)

    _copy_skill_markdown(package_dir)
    _write_scripts(package_dir)
    _copy_runtime_tree(package_dir)
    _copy_prompt_assets(package_dir)
    _vendor_chevron(package_dir)
    return package_dir


def _copy_skill_markdown(package_dir: Path) -> None:
    source_path = default_codex_package_dir() / "SKILL.md"
    destination_path = package_dir / "SKILL.md"
    if source_path.resolve() == destination_path.resolve():
        return
    shutil.copy2(source_path, destination_path)


def _write_scripts(package_dir: Path) -> None:
    scripts_dir = package_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    _write_script(scripts_dir / "init_topic_run.py", _init_topic_run_script())
    _write_script(scripts_dir / "prepare_stage.py", _prepare_stage_script())
    _write_script(scripts_dir / "apply_response.py", _apply_response_script())
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

os.environ.setdefault("QUESTION_GENERATOR_RUNTIME_ROOT", str(RUNTIME_ROOT))
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
    return ["run-topic", *args]


if __name__ == "__main__":
    raise SystemExit(main(_build_args()))
"""


def _init_topic_run_script() -> str:
    return _script_prelude() + """

if __name__ == "__main__":
    raise SystemExit(main(["init-topic-run", *sys.argv[1:]]))
"""


def _prepare_stage_script() -> str:
    return _script_prelude() + """

if __name__ == "__main__":
    raise SystemExit(main(["prepare-stage", *sys.argv[1:]]))
"""


def _apply_response_script() -> str:
    return _script_prelude() + """

if __name__ == "__main__":
    raise SystemExit(main(["apply-response", *sys.argv[1:]]))
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
    return ["run-recipe-on-run", *args]


if __name__ == "__main__":
    raise SystemExit(main(_build_args()))
"""


def refresh_codex_package(*, output_dir: Path | None = None) -> Path:
    return build_codex_package(output_dir=output_dir)
