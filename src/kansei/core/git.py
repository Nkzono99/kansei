from __future__ import annotations

import subprocess
from pathlib import Path


def init_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True, text=True)


def is_git_repo(root: Path) -> bool:
    return (root / ".git").exists()


def is_clean(root: Path) -> bool:
    if not is_git_repo(root):
        return True
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == ""

