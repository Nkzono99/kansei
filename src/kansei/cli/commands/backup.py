from __future__ import annotations

from pathlib import Path
from typing import Annotated
from zipfile import ZIP_DEFLATED, ZipFile

import typer

from kansei.core.paths import find_instance_root
from kansei.core.time import now_iso

BACKUP_INCLUDE = (
    "README.md",
    "AGENTS.md",
    "KANSEI.md",
    "kansei.toml",
    "projects.toml",
    "providers.toml",
    "knowledge",
    "dashboards",
    "runbooks",
    "prompts",
    ".codex",
    ".kansei/manifest.toml",
    ".kansei/lock.toml",
)


def backup(
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
    output: Annotated[Path | None, typer.Option("--output", help="Backup zip path.")] = None,
) -> None:
    """Create a local zip backup of the Kansei instance control-plane files."""
    instance_root = root.resolve() if root else find_instance_root()
    backup_path = output or _default_backup_path(instance_root)
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(backup_path, "w", compression=ZIP_DEFLATED) as archive:
        for relative in _iter_backup_files(instance_root):
            archive.write(instance_root / relative, relative.as_posix())

    typer.echo(str(backup_path))


def _default_backup_path(root: Path) -> Path:
    stamp = now_iso().replace(":", "").replace("+", "-")
    return root / ".kansei" / "backups" / f"kansei-backup-{stamp}.zip"


def _iter_backup_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for raw in BACKUP_INCLUDE:
        path = root / raw
        if path.is_file():
            files.append(Path(raw))
        elif path.is_dir():
            files.extend(
                child.relative_to(root)
                for child in path.rglob("*")
                if child.is_file() and ".kansei/backups" not in child.relative_to(root).as_posix()
            )
    return sorted(files)
