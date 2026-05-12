from __future__ import annotations

import json

import typer

from kansei.dashboard.generator import workspace_status


def status() -> None:
    typer.echo(json.dumps(workspace_status().model_dump(), indent=2))
