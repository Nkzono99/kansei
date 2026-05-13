from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

import typer

from kansei.cli.update_notice import maybe_emit_update_notice
from kansei.core.instance import find_instance_root
from kansei.core.lockfile import load_lock, sha256_file
from kansei.core.manifest import MANIFEST_PATH


@dataclass(frozen=True)
class DoctorReport:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


REQUIRED_FILES = (
    "kansei.toml",
    "projects.toml",
    "providers.toml",
    "AGENTS.md",
    "KANSEI.md",
    str(MANIFEST_PATH),
    ".kansei/lock.toml",
)

REQUIRED_DIRS = (
    "knowledge",
    "dashboards",
    "runbooks",
    "prompts",
    ".kansei/state",
    ".kansei/backups",
)


def run_doctor(root: Path) -> DoctorReport:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_FILES:
        if not (root / path).is_file():
            errors.append(f"missing file: {path}")
    for path in REQUIRED_DIRS:
        if not (root / path).is_dir():
            errors.append(f"missing directory: {path}")

    parsed: dict[str, dict[str, Any]] = {}
    for path in ("kansei.toml", "projects.toml", "providers.toml", str(MANIFEST_PATH)):
        file_path = root / path
        if not file_path.exists():
            continue
        try:
            data = tomllib.loads(file_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"invalid TOML in {path}: {exc}")
            continue
        parsed[path] = data
        if data.get("schema_version") != "0.1":
            errors.append(f"{path} has unsupported schema_version")

    _validate_projects(parsed.get("projects.toml", {}), errors)
    _validate_providers(parsed.get("providers.toml", {}), errors)

    for managed in load_lock(root).values():
        managed_path = root / managed.path
        if not managed_path.exists():
            errors.append(f"managed file missing: {managed.path}")
            continue
        if sha256_file(managed_path) != managed.checksum:
            warnings.append(f"managed file has local edits: {managed.path}")

    return DoctorReport(ok=not errors, errors=tuple(errors), warnings=tuple(warnings))


def _validate_projects(data: dict[str, object], errors: list[str]) -> None:
    projects = data.get("projects", [])
    if not isinstance(projects, list):
        errors.append("projects.toml projects must be a list")
        return

    seen: set[str] = set()
    required = {"id", "name", "kind", "provider", "location", "path"}
    for index, project in enumerate(projects, start=1):
        if not isinstance(project, dict):
            errors.append(f"project #{index} must be a table")
            continue
        missing = sorted(required - project.keys())
        if missing:
            errors.append(f"project #{index} missing fields: {', '.join(missing)}")
        project_id = project.get("id")
        if isinstance(project_id, str):
            if project_id in seen:
                errors.append(f"duplicate project id: {project_id}")
            seen.add(project_id)
        if project.get("location") == "ssh" and "host" not in project:
            errors.append(f"ssh project missing host: {project_id or index}")


def _validate_providers(data: dict[str, object], errors: list[str]) -> None:
    providers = data.get("providers", {})
    if not isinstance(providers, dict):
        errors.append("providers.toml providers must be a table")
        return
    for provider_id, provider in providers.items():
        if not isinstance(provider, dict):
            errors.append(f"provider {provider_id} must be a table")
            continue
        for field in ("type", "mode"):
            if field not in provider:
                errors.append(f"provider {provider_id} missing field: {field}")
        if provider.get("mode") in {"cli", "stdio"} and "command" not in provider:
            errors.append(f"provider {provider_id} missing field: command")
        if provider.get("mode") == "streamable-http" and "url" not in provider:
            errors.append(f"provider {provider_id} missing field: url")


def doctor(
    root: Annotated[Path | None, typer.Option("--root", help="Kansei instance root.")] = None,
    check_projects: Annotated[
        bool,
        typer.Option("--check-projects", help="Validate project registry."),
    ] = True,
    check_providers: Annotated[
        bool,
        typer.Option("--check-providers", help="Validate provider registry."),
    ] = True,
    check_mcp: Annotated[bool, typer.Option("--check-mcp", help="Validate MCP config.")] = False,
    check_codex: Annotated[
        bool,
        typer.Option("--check-codex", help="Validate Codex config."),
    ] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    instance_root = root.resolve() if root else find_instance_root()
    report = run_doctor(instance_root)
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "ok": report.ok,
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "checks": {
                        "projects": check_projects,
                        "providers": check_providers,
                        "mcp": check_mcp,
                        "codex": check_codex,
                    },
                },
                indent=2,
            )
        )
        if not report.ok:
            raise typer.Exit(1)
        return
    for warning in report.warnings:
        typer.echo(f"warning: {warning}")
    for error in report.errors:
        typer.echo(f"error: {error}", err=True)
    if not report.ok:
        raise typer.Exit(1)
    typer.echo(f"Kansei doctor passed: {instance_root}")
    maybe_emit_update_notice(command="doctor", root=instance_root)
