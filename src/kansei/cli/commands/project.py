from __future__ import annotations

import json
from typing import Annotated

import typer

from kansei.registry.projects import Project, add_project, load_projects

app = typer.Typer(help="Manage project registry.", no_args_is_help=True)


@app.command("list")
def list_projects(
    active: Annotated[bool | None, typer.Option()] = None,
    kind: Annotated[str | None, typer.Option()] = None,
    priority: Annotated[str | None, typer.Option()] = None,
) -> None:
    registry = load_projects()
    typer.echo(
        json.dumps(
            [
                project.model_dump()
                for project in registry.list(active=active, kind=kind, priority=priority)
            ],
            indent=2,
        )
    )


@app.command("show")
def show_project(project_id: str) -> None:
    typer.echo(json.dumps(load_projects().get(project_id).model_dump(), indent=2))


@app.command("add")
def add_project_command(
    id: Annotated[str, typer.Option("--id")],
    name: Annotated[str, typer.Option("--name")],
    kind: Annotated[str, typer.Option("--kind")],
    provider: Annotated[str, typer.Option("--provider")],
    location: Annotated[str, typer.Option("--location")],
    path: Annotated[str, typer.Option("--path")],
    host: Annotated[str | None, typer.Option("--host")] = None,
    priority: Annotated[str, typer.Option("--priority")] = "C",
    active: Annotated[bool, typer.Option("--active/--inactive")] = True,
) -> None:
    project = Project.model_validate(
        {
            "id": id,
            "name": name,
            "kind": kind,
            "provider": provider,
            "location": location,
            "path": path,
            "host": host,
            "priority": priority,
            "active": active,
        }
    )
    add_project(project)
    typer.echo(f"added project: {project.id}")
