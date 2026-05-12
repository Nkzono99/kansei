#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_FILES = [
    "AGENTS.md",
    "KANSEI.md",
    "kansei.toml",
    "projects.toml",
    "providers.toml",
    ".kansei/manifest.toml",
    ".kansei/lock.toml",
]

REQUIRED_DIRS = [
    "knowledge",
    "dashboards",
    "runbooks",
    "prompts",
]


def _missing(root: Path, entries: list[str], *, want_dir: bool) -> list[str]:
    missing: list[str] = []
    for item in entries:
        path = root / item
        wrong_kind = (want_dir and not path.is_dir()) or (not want_dir and not path.is_file())
        if not path.exists() or wrong_kind:
            missing.append(item)
    return missing


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_instance.py <instance-root>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    missing_files = _missing(root, REQUIRED_FILES, want_dir=False)
    missing_dirs = _missing(root, REQUIRED_DIRS, want_dir=True)
    has_root_markers = not {"kansei.toml", ".kansei/manifest.toml"} & set(missing_files)
    result = {
        "root": str(root),
        "status": "ok" if not missing_files and not missing_dirs else "missing",
        "is_instance_root": has_root_markers,
        "missing_files": missing_files,
        "missing_dirs": missing_dirs,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
