from __future__ import annotations

import typer

from kansei.dashboard.renderer import render_today, render_weekly, write_today, write_weekly

app = typer.Typer(help="Render dashboard views.", no_args_is_help=True)


@app.command("today")
def today(write: bool = False) -> None:
    if write:
        path = write_today()
        typer.echo(str(path))
        return
    typer.echo(render_today())


@app.command("weekly")
def weekly(write: bool = False) -> None:
    if write:
        path = write_weekly()
        typer.echo(str(path))
        return
    typer.echo(render_weekly())
