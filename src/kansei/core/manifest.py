from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from kansei import __version__
from kansei.core.time import now_iso

MANIFEST_PATH = Path(".kansei") / "manifest.toml"


def default_manifest(root: Path, *, template_version: str = "0.1.0") -> dict[str, object]:
    return {
        "schema_version": "0.1",
        "instance": {
            "name": root.name,
            "root": ".",
            "created_at": now_iso(),
            "created_by": f"kansei {__version__}",
        },
        "harness": {
            "kansei_version": __version__,
            "template_version": template_version,
            "layout_version": "0.1",
        },
        "paths": {
            "projects": "projects.toml",
            "providers": "providers.toml",
            "knowledge": "knowledge",
            "dashboards": "dashboards",
            "runbooks": "runbooks",
        },
        "policy": {
            "protect_user_files": True,
            "require_git_clean_for_apply": True,
        },
    }


def read_manifest(root: Path) -> dict[str, object]:
    return tomllib.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def write_manifest(root: Path, manifest: dict[str, object]) -> None:
    path = root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomli_w.dumps(manifest), encoding="utf-8")

