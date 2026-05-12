from __future__ import annotations

from pathlib import Path

from kansei.core.errors import InstanceNotFoundError

ROOT_MARKERS = ("kansei.toml", ".kansei/manifest.toml")


def find_instance_root(start: Path | str | None = None) -> Path:
    """Find a Kansei instance by walking upward from start or cwd."""
    current = Path(start or Path.cwd()).expanduser().resolve()
    if current.is_file():
        current = current.parent

    for path in (current, *current.parents):
        if any((path / marker).exists() for marker in ROOT_MARKERS):
            return path

    raise InstanceNotFoundError(f"not inside a Kansei instance: {current}")


def resolve_instance_path(root: Path, raw_path: str | Path) -> Path:
    """Resolve a user path relative to the instance root."""
    path = Path(str(raw_path)).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (root / path).resolve()


def relative_to_root(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)
