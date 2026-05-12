from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from kansei.core.instance import find_instance_root
from kansei.update.applier import apply_update
from kansei.update.planner import plan_update


def update_harness(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Apply planned managed-file updates."),
    ] = False,
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
) -> None:
    instance_root = root.resolve() if root else find_instance_root()
    plan = plan_update(instance_root)

    for action in plan.actions:
        if action.action == "unchanged":
            continue
        suffix = f" -> {action.new_path}" if action.new_path else ""
        typer.echo(f"{action.action}: {action.path}{suffix} ({action.reason})")

    if not plan.has_changes:
        typer.echo("Kansei harness is up to date.")
        return

    if not apply:
        typer.echo("Dry run only. Re-run with --apply to write changes.")
        return

    apply_update(plan)
    typer.echo("Kansei harness update applied.")
