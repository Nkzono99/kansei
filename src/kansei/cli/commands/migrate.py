from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, cast

import typer

from kansei.core.manifest import read_manifest
from kansei.core.paths import find_instance_root


def migrate(
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Inspect migration status for the current layout version."""
    instance_root = root.resolve() if root else find_instance_root()
    manifest = read_manifest(instance_root)
    harness = cast(dict[str, Any], manifest.get("harness", {}))
    report = {
        "root": str(instance_root),
        "status": "ok",
        "schema_version": manifest.get("schema_version"),
        "layout_version": harness.get("layout_version"),
        "pending": [],
    }
    if json_output:
        typer.echo(json.dumps(report, indent=2))
        return
    typer.echo("No migrations pending.")
