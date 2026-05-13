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
from kansei.core.instance import TEMPLATE_VERSION, find_instance_root
from kansei.core.manifest import record_applied_harness_metadata
from kansei.update.applier import apply_update
from kansei.update.chain import (
    UpgradeChain,
    UpgradeChainError,
    build_upgrade_chain,
    run_upgrade_chain,
)
from kansei.update.planner import plan_update


def update_harness(
    apply: Annotated[
        bool,
        typer.Option("--apply", help="Apply planned managed-file updates."),
    ] = False,
    plan_chain: Annotated[
        bool,
        typer.Option("--plan", help="Show a versioned uvx upgrade chain without writing."),
    ] = False,
    apply_chain: Annotated[
        bool,
        typer.Option("--apply-chain", help="Run checkpoint updates via exact uvx versions."),
    ] = False,
    target: Annotated[
        str,
        typer.Option("--target", help="Upgrade chain target version, minor prefix, or latest."),
    ] = "latest",
    allow_major: Annotated[
        bool,
        typer.Option("--allow-major", help="Allow --apply-chain to cross a major version."),
    ] = False,
    upgrade_step: Annotated[
        bool,
        typer.Option(
            "--upgrade-step",
            help="Internal exact-version chain step; applies this runtime's harness update.",
        ),
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
    if apply and (plan_chain or apply_chain):
        typer.echo("--apply cannot be combined with --plan or --apply-chain", err=True)
        raise typer.Exit(2)
    if plan_chain and apply_chain:
        typer.echo("--plan and --apply-chain cannot be used together", err=True)
        raise typer.Exit(2)
    if upgrade_step and (plan_chain or apply_chain):
        typer.echo("--upgrade-step cannot be combined with --plan or --apply-chain", err=True)
        raise typer.Exit(2)

    if upgrade_step:
        _run_local_update(
            instance_root,
            apply=True,
            harnessops=False,
            harnessops_profile=harnessops_profile,
            with_harnessops_agent_bridge=with_harnessops_agent_bridge,
            require_harnessops=False,
        )
        return

    if plan_chain or apply_chain:
        try:
            chain = build_upgrade_chain(instance_root, target=target)
            _echo_upgrade_chain(chain)
            if apply_chain:
                for result in run_upgrade_chain(chain, allow_major=allow_major):
                    typer.echo(
                        f"Kansei upgrade step applied: "
                        f"{result.step.from_version} -> {result.step.to_version}"
                    )
                    if result.stdout.strip():
                        typer.echo(result.stdout.rstrip())
                    if result.stderr.strip():
                        typer.echo(result.stderr.rstrip(), err=True)
                if not chain.has_steps:
                    typer.echo("Kansei upgrade chain is empty.")
                if harnessops:
                    _run_harnessops_update(
                        instance_root,
                        apply=True,
                        profile=harnessops_profile,
                        with_agent_bridge=with_harnessops_agent_bridge,
                        required=require_harnessops,
                    )
        except UpgradeChainError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1) from exc
        return

    _run_local_update(
        instance_root,
        apply=apply,
        harnessops=harnessops,
        harnessops_profile=harnessops_profile,
        with_harnessops_agent_bridge=with_harnessops_agent_bridge,
        require_harnessops=require_harnessops,
    )


def _run_local_update(
    instance_root: Path,
    *,
    apply: bool,
    harnessops: bool,
    harnessops_profile: str,
    with_harnessops_agent_bridge: bool,
    require_harnessops: bool,
) -> None:
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
        if apply:
            record_applied_harness_metadata(instance_root, template_version=TEMPLATE_VERSION)
            typer.echo("Kansei harness metadata refreshed.")
    elif not apply:
        typer.echo("Dry run only. Re-run with --apply to write changes.")
    else:
        apply_update(plan)
        typer.echo("Kansei harness update applied.")

    if not harnessops:
        return

    _run_harnessops_update(
        instance_root,
        apply=apply,
        profile=harnessops_profile,
        with_agent_bridge=with_harnessops_agent_bridge,
        required=require_harnessops,
    )


def _run_harnessops_update(
    instance_root: Path,
    *,
    apply: bool,
    profile: str,
    with_agent_bridge: bool,
    required: bool,
) -> None:
    try:
        for result in run_harnessops_update(
            instance_root,
            apply=apply,
            profile=profile,
            with_agent_bridge=with_agent_bridge,
            required=required,
        ):
            _echo_harnessops_result(result)
    except HarnessOpsError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


def _echo_upgrade_chain(chain: UpgradeChain) -> None:
    typer.echo(f"current instance artifacts: {chain.applied_version or 'unknown'}")
    typer.echo(f"current Kansei runtime:      {chain.current_version}")
    typer.echo(f"target Kansei version:      {chain.target_version} ({chain.target_source})")
    if not chain.has_steps:
        typer.echo("planned upgrade chain: empty")
        return
    typer.echo("planned upgrade chain:")
    for index, step in enumerate(chain.steps, start=1):
        marker = " [major]" if step.crosses_major else ""
        typer.echo(f"{index}. {step.from_version} -> {step.to_version}{marker}")


def _echo_harnessops_result(result: HarnessOpsResult) -> None:
    if result.ran:
        typer.echo(f"HarnessOps: ran hops {' '.join(result.args)}")
        if result.stdout.strip():
            typer.echo(result.stdout.rstrip())
        if result.stderr.strip():
            typer.echo(result.stderr.rstrip(), err=True)
        return
    typer.echo(f"HarnessOps: skipped hops {' '.join(result.args)} ({result.reason})")
