from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from kansei.cli.update_notice import maybe_emit_update_notice
from kansei.core.bootstrap import (
    DEFAULT_INSTALL_SPEC,
    BootstrapError,
    BootstrapResult,
    bootstrap_environment,
)
from kansei.core.harnessops import (
    DEFAULT_PROJECT_PROFILE,
    HarnessOpsError,
    HarnessOpsResult,
    hops_is_available,
    run_harnessops_init,
)
from kansei.core.instance import init_instance
from kansei.core.manifest import kansei_uvx_command

app = typer.Typer(help="Initialize a private Kansei instance.")


@app.callback(invoke_without_command=True)
def init(
    target: Annotated[Path, typer.Argument(help="Target directory for the Kansei instance.")],
    git: Annotated[bool, typer.Option("--git", help="Initialize a git repository.")] = False,
    with_codex: Annotated[
        bool,
        typer.Option("--with-codex", help="Write .codex/config.toml."),
    ] = False,
    with_mcp: Annotated[
        bool,
        typer.Option("--with-mcp", help="Enable MCP defaults in config."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Allow initializing an existing instance."),
    ] = False,
    bootstrap: Annotated[
        bool,
        typer.Option(
            "--bootstrap/--no-bootstrap",
            help="Legacy opt-in: create .venv and install Kansei into the generated instance.",
        ),
    ] = False,
    kansei_install_spec: Annotated[
        str,
        typer.Option(
            "--kansei-install-spec",
            help="Legacy package spec installed into .venv when --bootstrap is used.",
        ),
    ] = DEFAULT_INSTALL_SPEC,
    require_bootstrap: Annotated[
        bool,
        typer.Option("--require-bootstrap", help="Fail if .venv bootstrap cannot complete."),
    ] = False,
    harnessops: Annotated[
        bool,
        typer.Option(
            "--harnessops/--no-harnessops",
            help="Run hops init in the generated Kansei instance when available.",
        ),
    ] = True,
    harnessops_profile: Annotated[
        str,
        typer.Option("--harnessops-profile", help="HarnessOps profile for the generated instance."),
    ] = DEFAULT_PROJECT_PROFILE,
    with_harnessops_agent_bridge: Annotated[
        bool,
        typer.Option(
            "--with-harnessops-agent-bridge",
            help="Pass --with-agent-bridge to hops init.",
        ),
    ] = False,
    require_harnessops: Annotated[
        bool,
        typer.Option("--require-harnessops", help="Fail if the chained hops command cannot run."),
    ] = False,
) -> None:
    if harnessops and require_harnessops and not hops_is_available():
        typer.echo(
            "hops command not found; install HarnessOps, set KANSEI_HOPS_COMMAND, "
            "or set KANSEI_HARNESSOPS_SOURCE",
            err=True,
        )
        raise typer.Exit(1)

    root = init_instance(
        target,
        use_git=git,
        with_codex=with_codex,
        with_mcp=with_mcp,
        force=force,
    )
    typer.echo(f"Initialized Kansei instance at {root}")
    if bootstrap:
        try:
            _echo_bootstrap_result(
                bootstrap_environment(
                    root,
                    install_spec=kansei_install_spec,
                    required=require_bootstrap,
                )
            )
        except BootstrapError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1) from exc
    else:
        _echo_uvx_next_steps(root)

    if not harnessops:
        maybe_emit_update_notice(command="init", root=root)
        return
    try:
        for result in run_harnessops_init(
            root,
            profile=harnessops_profile,
            with_agent_bridge=with_harnessops_agent_bridge,
            required=require_harnessops,
        ):
            _echo_harnessops_result(result)
    except HarnessOpsError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    maybe_emit_update_notice(command="init", root=root)


def _echo_harnessops_result(result: HarnessOpsResult) -> None:
    if result.ran:
        typer.echo(f"HarnessOps: ran hops {' '.join(result.args)}")
        if result.stdout.strip():
            typer.echo(result.stdout.rstrip())
        if result.stderr.strip():
            typer.echo(result.stderr.rstrip(), err=True)
        return
    typer.echo(f"HarnessOps: skipped hops {' '.join(result.args)} ({result.reason})")


def _echo_bootstrap_result(result: BootstrapResult) -> None:
    for path in result.created:
        typer.echo(f"Bootstrap: created {path}")
    for path in result.skipped:
        typer.echo(f"Bootstrap: skipped {path}")
    for warning in result.warnings:
        typer.echo(f"Bootstrap warning: {warning}", err=True)
    typer.echo(f"Bootstrap next: {result.activation_hint}")


def _echo_uvx_next_steps(root: Path) -> None:
    typer.echo(f"Next: cd {root}")
    typer.echo(f"Next: {kansei_uvx_command('doctor')}")
