from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

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
