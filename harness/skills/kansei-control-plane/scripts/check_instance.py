#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = [
    "AGENTS.md",
    "KANSEI.md",
    "kansei.toml",
    "projects.toml",
    "providers.toml",
    ".kansei/manifest.toml",
    ".kansei/lock.toml",
    "knowledge",
    "dashboards",
    "runbooks",
    "prompts",
]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_instance.py <instance-root>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    missing = [item for item in REQUIRED if not (root / item).exists()]
    result = {
        "root": str(root),
        "status": "ok" if not missing else "missing",
        "missing": missing,
    }
    print(json.dumps(result, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
