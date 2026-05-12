from __future__ import annotations

import typer

from kansei import __version__
from kansei.cli.commands import dashboard, init, mcp, project, provider
from kansei.cli.commands import doctor as doctor_command
from kansei.cli.commands import search as search_command
from kansei.cli.commands import status as status_command
from kansei.cli.commands import update as update_command

app = typer.Typer(
    help="Kansei private control plane CLI.",
    no_args_is_help=True,
)

app.add_typer(project.app, name="project")
app.add_typer(provider.app, name="provider")
app.add_typer(dashboard.app, name="dashboard")
app.add_typer(mcp.app, name="mcp")
app.command("init")(init.init)
app.command()(doctor_command.doctor)
app.command()(status_command.status)
app.command()(search_command.search)
app.command("update-harness")(update_command.update_harness)


@app.command()
def version() -> None:
    """Print the Kansei package version."""
    typer.echo(__version__)
