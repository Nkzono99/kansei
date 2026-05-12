from __future__ import annotations

import json
import shlex
import subprocess
from typing import Annotated

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


@app.command("connect")
def connect(
    provider_id: str,
    tunnel: Annotated[bool, typer.Option("--tunnel", help="Plan or run SSH tunnel.")] = False,
    execute: Annotated[
        bool,
        typer.Option("--exec", help="Run the connection command in the foreground."),
    ] = False,
) -> None:
    provider = load_providers().get(provider_id)
    if not tunnel:
        typer.echo(json.dumps(provider.model_dump(exclude_none=True), indent=2))
        return
    if not provider.ssh_tunnel:
        raise typer.BadParameter(f"provider has no ssh_tunnel: {provider_id}")

    command = _ssh_tunnel_command(provider.ssh_tunnel)
    typer.echo(shlex.join(command))
    if execute:
        subprocess.run(command, check=False)


def _ssh_tunnel_command(spec: str) -> list[str]:
    parts = spec.split(":")
    if len(parts) != 4:
        raise typer.BadParameter("ssh_tunnel must be host:local_port:remote_host:remote_port")
    host, local_port, remote_host, remote_port = parts
    return ["ssh", "-N", "-L", f"{local_port}:{remote_host}:{remote_port}", host]
