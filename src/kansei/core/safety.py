from __future__ import annotations

from pathlib import Path


class KanseiSafetyError(RuntimeError):
    pass


def ensure_within_root(root: Path, target: Path) -> Path:
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    if resolved_target != resolved_root and resolved_root not in resolved_target.parents:
        raise KanseiSafetyError(f"target escapes Kansei root: {target}")
    return resolved_target

