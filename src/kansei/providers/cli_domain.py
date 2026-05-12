from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from kansei.providers.base import ProjectRef, ProjectStatus, ProviderHealth


class DomainCliProvider:
    provider_id: str
    command_name: str
    domain_name: str

    def __init__(self, provider_id: str, command_name: str, domain_name: str) -> None:
        self.provider_id = provider_id
        self.command_name = command_name
        self.domain_name = domain_name

    def health(self) -> ProviderHealth:
        command_path = shutil.which(self.command_name)
        if command_path:
            return ProviderHealth(
                provider_id=self.provider_id,
                status="ok",
                summary=f"{self.command_name} found at {command_path}",
            )
        return ProviderHealth(
            provider_id=self.provider_id,
            status="warning",
            summary=f"{self.command_name} CLI is not on PATH",
            warnings=[f"Install or configure {self.domain_name} before domain status calls."],
        )

    def status(self, project: ProjectRef) -> ProjectStatus:
        warnings = []
        if project.location == "local" and not Path(project.path).expanduser().exists():
            warnings.append(f"registered path does not exist: {project.path}")
        if project.location != "local":
            warnings.append(f"{project.location} status should be read through provider MCP/SSH.")
        return ProjectStatus(
            project_id=project.id,
            provider_id=self.provider_id,
            status="warning" if warnings else "unknown",
            summary=f"{self.domain_name} adapter is configured; domain status is plan-only in v0.1",
            warnings=warnings,
            next_actions=[
                {
                    "label": f"Delegate read-only {self.domain_name} status check",
                    "kind": "delegate-plan",
                }
            ],
            details={"domain": self.domain_name, "command": self.command_name},
        )

    def doctor(self, project: ProjectRef) -> ProjectStatus:
        health = self.health()
        status = self.status(project)
        warnings = [*health.warnings, *status.warnings]
        return status.model_copy(
            update={
                "status": "warning" if warnings else status.status,
                "warnings": warnings,
            }
        )

    def delegate_plan(self, project: ProjectRef, task: str) -> dict[str, Any]:
        command = ["codex", "exec", "--cd", project.path, task]
        if project.location == "ssh" and project.host:
            command = ["ssh", project.host, f"cd {project.path} && codex exec {task!r}"]
        return {
            "project_id": project.id,
            "provider_id": self.provider_id,
            "mode": "plan",
            "command": command,
            "requires_approval": True,
            "safety": {
                "remote_write_requires_explicit_approval": True,
                "hpc_submit_requires_explicit_approval": self.provider_id == "runops",
            },
        }
