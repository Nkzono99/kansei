from __future__ import annotations

import json
import tomllib
from pathlib import Path

from jsonschema import validate

from kansei.core.instance import init_instance


def test_public_json_schemas_validate_initialized_instance(tmp_path: Path) -> None:
    root = init_instance(tmp_path / "kansei", with_codex=True, with_mcp=True)
    repo_root = Path(__file__).resolve().parents[1]

    validate(_load_toml(root / "kansei.toml"), _load_json(repo_root / "schemas/kansei.schema.json"))
    validate(
        _load_toml(root / "projects.toml"),
        _load_json(repo_root / "schemas/projects.schema.json"),
    )
    validate(
        _load_toml(root / "providers.toml"),
        _load_json(repo_root / "schemas/providers.schema.json"),
    )
    validate(
        _load_toml(root / ".kansei/manifest.toml"),
        _load_json(repo_root / "schemas/manifest.schema.json"),
    )
    validate(
        _load_toml(root / ".kansei/lock.toml"),
        _load_json(repo_root / "schemas/lock.schema.json"),
    )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))
