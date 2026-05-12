from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from kansei.core.harnessops import (
    DEFAULT_PROJECT_PROFILE,
    HarnessOpsError,
    HarnessOpsResult,
    hops_is_available,
    run_harnessops_update,
)
from kansei.core.instance import find_instance_root
from kansei.update.applier import apply_update
from kansei.update.planner import plan_update


def update_harness(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Apply planned managed-file updates."),
    ] = False,
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
    harnessops: Annotated[
        bool,
        typer.Option(
            "--harnessops/--no-harnessops",
            help="Run hops update-harness for the instance when available.",
        ),
    ] = True,
    harnessops_profile: Annotated[
        str,
        typer.Option(
            "--harnessops-profile",
            help="HarnessOps profile to initialize older instances before updating.",
        ),
    ] = DEFAULT_PROJECT_PROFILE,
    with_harnessops_agent_bridge: Annotated[
        bool,
        typer.Option(
            "--with-harnessops-agent-bridge",
            help="Ask HarnessOps to check or deploy repo-local Codex bridge skills.",
        ),
    ] = False,
    require_harnessops: Annotated[
        bool,
        typer.Option("--require-harnessops", help="Fail if the chained hops command cannot run."),
    ] = False,
) -> None:
    instance_root = root.resolve() if root else find_instance_root()
    if harnessops and require_harnessops and not hops_is_available():
        typer.echo(
            "hops command not found; install HarnessOps, set KANSEI_HOPS_COMMAND, "
            "or set KANSEI_HARNESSOPS_SOURCE",
            err=True,
        )
        raise typer.Exit(1)

    plan = plan_update(instance_root)

    for action in plan.actions:
        if action.action == "unchanged":
            continue
        suffix = f" -> {action.new_path}" if action.new_path else ""
        typer.echo(f"{action.action}: {action.path}{suffix} ({action.reason})")

    if not plan.has_changes:
        typer.echo("Kansei harness is up to date.")
    elif not apply:
        typer.echo("Dry run only. Re-run with --apply to write changes.")
    else:
        apply_update(plan)
        typer.echo("Kansei harness update applied.")

    if not harnessops:
        return

    try:
        for result in run_harnessops_update(
            instance_root,
            apply=apply,
            profile=harnessops_profile,
            with_agent_bridge=with_harnessops_agent_bridge,
            required=require_harnessops,
        ):
            _echo_harnessops_result(result)
    except HarnessOpsError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _echo_harnessops_result(result: HarnessOpsResult) -> None:
    if result.ran:
        typer.echo(f"HarnessOps: ran hops {' '.join(result.args)}")
        if result.stdout.strip():
            typer.echo(result.stdout.rstrip())
        if result.stderr.strip():
            typer.echo(result.stderr.rstrip(), err=True)
        return
    typer.echo(f"HarnessOps: skipped hops {' '.join(result.args)} ({result.reason})")
