from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from kansei import __version__
from kansei.core.time import now_iso

MANIFEST_PATH = Path(".kansei") / "manifest.toml"
PACKAGE_NAME = "kansei"
CONSOLE_SCRIPT = "kansei"


def kansei_uvx_command(*args: str, refresh_package: bool = False) -> str:
    command = ["uvx"]
    if refresh_package:
        command.extend(("--refresh-package", PACKAGE_NAME))
    command.extend(("--from", PACKAGE_NAME, CONSOLE_SCRIPT, *args))
    return " ".join(_shell_arg(part) for part in command)


def default_manifest(root: Path, *, template_version: str = "0.1.0") -> dict[str, Any]:
    created_at = now_iso()
    return {
        "schema_version": "0.1",
        "instance": {
            "name": root.name,
            "root": ".",
            "created_at": created_at,
            "created_by": f"kansei {__version__}",
        },
        "harness": {
            "package": PACKAGE_NAME,
            "kansei_version": __version__,
            "template_version": template_version,
            "layout_version": "0.1",
        },
        "cli": {
            "package": PACKAGE_NAME,
            "version": __version__,
            "runner": "uvx",
            "command": kansei_uvx_command(),
            "updated_at": created_at,
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


def read_manifest(root: Path) -> dict[str, Any]:
    return tomllib.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))


def write_manifest(root: Path, manifest: dict[str, Any]) -> None:
    path = root / MANIFEST_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomli_w.dumps(manifest), encoding="utf-8")


def record_applied_harness_metadata(root: Path, *, template_version: str) -> None:
    manifest = read_manifest(root)
    updated_at = now_iso()

    harness = _as_table(manifest.get("harness"))
    harness["package"] = PACKAGE_NAME
    harness["kansei_version"] = __version__
    harness["template_version"] = template_version
    harness.setdefault("layout_version", "0.1")

    cli = _as_table(manifest.get("cli"))
    cli["package"] = PACKAGE_NAME
    cli["version"] = __version__
    cli["runner"] = "uvx"
    cli["command"] = kansei_uvx_command()
    cli["updated_at"] = updated_at

    manifest["harness"] = harness
    manifest["cli"] = cli
    write_manifest(root, manifest)


def applied_harness_kansei_version(root: Path) -> str | None:
    try:
        manifest = read_manifest(root)
    except OSError:
        return None
    harness = manifest.get("harness")
    if not isinstance(harness, dict):
        return None
    version = harness.get("kansei_version")
    return version if isinstance(version, str) and version else None


def _as_table(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {str(key): item for key, item in value.items()}


def _shell_arg(value: str) -> str:
    if value and not any(char.isspace() for char in value):
        return value
    return '"' + value.replace('"', '\\"') + '"'
