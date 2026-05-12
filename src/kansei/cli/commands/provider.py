from __future__ import annotations

import json

import typer

from kansei.providers.generic_code import GenericCodeProvider
from kansei.registry.providers import load_providers

app = typer.Typer(help="Inspect provider registry.", no_args_is_help=True)


@app.command("list")
def list_providers() -> None:
    registry = load_providers()
    payload = {
        provider_id: provider.model_dump(exclude_none=True)
        for provider_id, provider in registry.list().items()
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("doctor")
def doctor(provider_id: str = "generic-code") -> None:
    health = GenericCodeProvider(provider_id=provider_id).health()
    typer.echo(json.dumps(health.model_dump(), indent=2))
