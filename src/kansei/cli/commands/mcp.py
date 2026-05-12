from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from kansei.core.paths import find_instance_root
from kansei.mcp.config import inspect_mcp_config, plan_codex_config, write_codex_config
from kansei.mcp.server import run

app = typer.Typer(help="Run the Kansei MCP server.", no_args_is_help=True)


@app.command()
def serve(
    transport: Annotated[
        str,
        typer.Option("--transport", help="stdio or streamable-http."),
    ] = "stdio",
    host: Annotated[str, typer.Option("--host", help="HTTP bind host.")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", help="HTTP bind port.")] = 18764,
    workspace: Annotated[
        Path | None,
        typer.Option(
            "--workspace",
            exists=False,
            file_okay=False,
            dir_okay=True,
            help="Kansei workspace root. Defaults to the current directory or nearest parent.",
        ),
    ] = None,
) -> None:
    """Serve read-only Kansei MCP tools and resources."""
    run(transport=transport, host=host, port=port, workspace_root=workspace)


@app.command("config")
def config(
    write: Annotated[
        bool,
        typer.Option("--write", help="Write .codex/config.toml instead of previewing."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite an existing differing generated config."),
    ] = False,
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
) -> None:
    """Render Codex MCP config from providers.toml."""
    instance_root = root.resolve() if root else find_instance_root()
    plan = plan_codex_config(instance_root)
    if not write:
        typer.echo(plan.content)
        return
    path = write_codex_config(plan, force=force)
    typer.echo(f"Wrote {path}")


@app.command("inspect")
def inspect(
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
) -> None:
    """Inspect the generated MCP/Codex configuration surface."""
    instance_root = root.resolve() if root else find_instance_root()
    typer.echo(json.dumps(inspect_mcp_config(instance_root), indent=2))
