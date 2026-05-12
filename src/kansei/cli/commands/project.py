from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from kansei.core.paths import find_instance_root, resolve_instance_path
from kansei.dashboard.generator import workspace_status
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


@app.command("open")
def open_project(
    project_id: str,
    execute: Annotated[
        bool,
        typer.Option("--exec", help="Open the local path with the operating system."),
    ] = False,
) -> None:
    root = find_instance_root()
    project = load_projects(root).get(project_id)
    if project.location == "local":
        path = resolve_instance_path(root, project.path)
        if execute:
            _open_local_path(path)
        typer.echo(str(path))
        return
    if project.location == "ssh" and project.host:
        typer.echo(f"{project.host}:{project.path}")
        return
    typer.echo(project.path)


@app.command("status")
def project_status(project_id: str) -> None:
    status = workspace_status(active=None)
    for project in status.projects:
        if project.project_id == project_id:
            typer.echo(json.dumps(project.model_dump(), indent=2))
            return
    raise typer.BadParameter(f"unknown project: {project_id}")


@app.command("doctor")
def project_doctor(project_id: str) -> None:
    status = workspace_status(active=None)
    for project in status.projects:
        if project.project_id == project_id:
            typer.echo(json.dumps(project.model_dump(), indent=2))
            if project.status == "error":
                raise typer.Exit(5)
            return
    raise typer.BadParameter(f"unknown project: {project_id}")


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


def _open_local_path(path: Path) -> None:
    if not path.exists():
        raise typer.BadParameter(f"path does not exist: {path}")
    typer.launch(str(path))
