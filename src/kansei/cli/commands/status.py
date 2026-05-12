from __future__ import annotations

import json
from typing import Annotated

import typer

from kansei.dashboard.generator import workspace_status


def status(
    project: Annotated[str | None, typer.Option("--project", help="Project id filter.")] = None,
    priority: Annotated[str | None, typer.Option("--priority", help="Priority filter.")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = True,
) -> None:
    report = workspace_status(active=None if project else True, priority=priority)
    if project:
        report = report.model_copy(
            update={"projects": [item for item in report.projects if item.project_id == project]}
        )
    if json_output:
        typer.echo(json.dumps(report.model_dump(), indent=2))
        return
    typer.echo(report.summary)
