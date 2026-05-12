from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from kansei.core.instance import init_instance

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
) -> None:
    root = init_instance(
        target,
        use_git=git,
        with_codex=with_codex,
        with_mcp=with_mcp,
        force=force,
    )
    typer.echo(f"Initialized Kansei instance at {root}")
