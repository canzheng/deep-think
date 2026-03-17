from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.question_generator.pathing import repo_root


OpenClawExecutorMode = Literal["session", "llm-task"]
DEFAULT_OPENCLAW_EXECUTOR_MODE: OpenClawExecutorMode = "session"
OPENCLAW_RUNTIME_CONFIG_PATH_ENV_VAR = "QUESTION_GENERATOR_OPENCLAW_CONFIG_PATH"
RUNTIME_CONFIG_FILENAME = "runtime.json"
RUNTIME_EXECUTOR_MODE_KEY = "json_executor"


@dataclass(frozen=True)
class OpenClawRuntimeConfig:
    executor_mode: OpenClawExecutorMode


def resolve_runtime_config_path(config_path: str | Path | None = None) -> Path:
    if config_path is not None:
        return Path(config_path).expanduser().resolve()
    env_override = os.environ.get(OPENCLAW_RUNTIME_CONFIG_PATH_ENV_VAR)
    if env_override:
        return Path(env_override).expanduser().resolve()
    return repo_root() / "skills" / "deep-think" / "openclaw" / "config" / RUNTIME_CONFIG_FILENAME


def normalize_executor_mode(mode: str | None) -> OpenClawExecutorMode:
    if mode is None:
        return DEFAULT_OPENCLAW_EXECUTOR_MODE

    normalized = str(mode).strip().lower().replace("-", "_")
    if normalized in {"llm_task", "llm-task", "llmtask"}:
        return "llm-task"
    if normalized in {"session", "native_session", "native-session", "session_fallback", "session-fallback"}:
        return "session"
    if normalized in {"chat_fallback", "chat-fallback", "chatfallback", "auto"}:
        return "session"
    return DEFAULT_OPENCLAW_EXECUTOR_MODE


def read_runtime_config(config_path: str | Path | None = None) -> OpenClawRuntimeConfig:
    path = resolve_runtime_config_path(config_path)
    if not path.is_file():
        return OpenClawRuntimeConfig(executor_mode=DEFAULT_OPENCLAW_EXECUTOR_MODE)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return OpenClawRuntimeConfig(executor_mode=DEFAULT_OPENCLAW_EXECUTOR_MODE)

    if isinstance(payload, dict):
        raw_mode = payload.get(RUNTIME_EXECUTOR_MODE_KEY)
    else:
        raw_mode = payload
    return OpenClawRuntimeConfig(executor_mode=normalize_executor_mode(raw_mode))


def write_runtime_config(
    config_path: str | Path | None = None,
    executor_mode: str = DEFAULT_OPENCLAW_EXECUTOR_MODE,
) -> None:
    path = resolve_runtime_config_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {RUNTIME_EXECUTOR_MODE_KEY: normalize_executor_mode(executor_mode)},
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
