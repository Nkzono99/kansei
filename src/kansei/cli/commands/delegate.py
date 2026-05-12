from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Annotated, Any

import typer

from kansei.core.paths import find_instance_root, resolve_instance_path
from kansei.providers.base import ProjectRef
from kansei.registry.discovery import get_builtin_provider
from kansei.registry.projects import Project, load_projects


def delegate(
    project_id: str,
    task: str,
    execute: Annotated[
        bool,
        typer.Option("--exec", help="Execute the delegation command instead of printing a plan."),
    ] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Print the raw JSON plan.")] = False,
) -> None:
    """Plan or run safe Codex delegation for a registered project."""
    root = find_instance_root()
    project = load_projects(root).get(project_id)
    adapter = get_builtin_provider(project.provider)
    plan = adapter.delegate_plan(_project_ref(project, root), task)

    if json_output:
        typer.echo(json.dumps(plan, indent=2))
    else:
        _print_plan(plan)

    if execute:
        if plan.get("requires_approval", True):
            typer.echo("Executing because --exec was provided.")
        subprocess.run([str(part) for part in plan["command"]], check=False)


def _project_ref(project: Project, root: Path) -> ProjectRef:
    path = project.path
    if project.location == "local":
        path = str(resolve_instance_path(root, project.path))
    return ProjectRef(
        id=project.id,
        name=project.name,
        kind=project.kind,
        provider=project.provider,
        location=project.location,
        path=path,
        host=project.host,
        priority=project.priority,
        active=project.active,
        tags=project.tags,
        notes=project.notes,
    )


def _print_plan(plan: dict[str, Any]) -> None:
    typer.echo(f"project: {plan['project_id']}")
    typer.echo(f"provider: {plan['provider_id']}")
    typer.echo(f"mode: {plan.get('mode', 'plan')}")
    typer.echo(f"requires_approval: {str(plan.get('requires_approval', True)).lower()}")
    typer.echo(f"command: {shlex.join(str(part) for part in plan['command'])}")
