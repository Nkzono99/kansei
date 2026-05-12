from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from kansei.core.errors import ConfigError
from kansei.core.paths import find_instance_root


class WorkspaceConfig(BaseModel):
    name: str = "Kansei"
    description: str = "Private control plane for AI-assisted research operations."
    timezone: str = "Asia/Tokyo"
    default_dashboard: str = "dashboards/today.md"


class PrivacyConfig(BaseModel):
    default_visibility: Literal["private", "internal", "public"] = "private"
    allow_public_export: bool = False
    sanitize_before_feedback: bool = True


class SafetyConfig(BaseModel):
    default_apply_requires_confirmation: bool = True
    protect_user_files: bool = True
    require_git_clean_for_apply: bool = True
    hpc_submit_requires_explicit_approval: bool = True
    remote_write_requires_explicit_approval: bool = True


class KanseiConfig(BaseModel):
    schema_version: str = "0.1"
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)


def load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"missing config file: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML in {path}: {exc}") from exc


def load_config(root: Path | str | None = None) -> KanseiConfig:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    path = instance_root / "kansei.toml"
    if not path.exists():
        return KanseiConfig()
    return KanseiConfig.model_validate(load_toml(path))
