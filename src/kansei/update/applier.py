from __future__ import annotations

from kansei.core.lockfile import load_lock, write_lock
from kansei.update.planner import UpdatePlan, managed_file_for


def apply_update(plan: UpdatePlan) -> None:
    lock = load_lock(plan.root)
    for action in plan.actions:
        if action.action == "unchanged":
            continue
        if action.action in {"create", "update"}:
            destination = plan.root / action.path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(action.content.encode("utf-8"))
            lock[action.path] = managed_file_for(action)
            continue
        if action.action == "write_new":
            assert action.new_path is not None
            destination = plan.root / action.new_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(action.content.encode("utf-8"))

    write_lock(plan.root, lock)
