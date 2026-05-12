from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from kansei.providers.base import ProjectRef, ProjectStatus, ProviderHealth


class GenericCodeProvider:
    def __init__(self, provider_id: str = "generic-code") -> None:
        self.provider_id = provider_id

    def health(self) -> ProviderHealth:
        result = _run(["git", "--version"], cwd=None)
        if result.returncode == 0:
            return ProviderHealth(
                provider_id=self.provider_id,
                status="ok",
                summary=result.stdout.strip(),
            )
        return ProviderHealth(
            provider_id=self.provider_id,
            status="error",
            summary="git is not available",
            warnings=[result.stderr.strip() or "git command failed"],
        )

    def status(self, project: ProjectRef) -> ProjectStatus:
        if project.location != "local":
            return ProjectStatus(
                project_id=project.id,
                provider_id=self.provider_id,
                status="skipped",
                summary=f"{project.location} projects require a domain provider",
                warnings=["generic-code only inspects local paths"],
            )

        path = Path(project.path).expanduser()
        if not path.exists():
            return ProjectStatus(
                project_id=project.id,
                provider_id=self.provider_id,
                status="error",
                summary=f"path does not exist: {path}",
                warnings=["registered project path is missing"],
            )

        inside = _run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"], cwd=None)
        if inside.returncode != 0:
            return ProjectStatus(
                project_id=project.id,
                provider_id=self.provider_id,
                status="warning",
                summary="local path is not a git worktree",
                warnings=[inside.stderr.strip() or "not a git worktree"],
                next_actions=[{"label": "Check project path", "kind": "inspect"}],
            )

        branch_result = _run(["git", "-C", str(path), "branch", "--show-current"], cwd=None)
        branch = branch_result.stdout.strip() or "detached"
        status_result = _run(["git", "-C", str(path), "status", "--porcelain=v1", "-b"], cwd=None)
        if status_result.returncode != 0:
            return ProjectStatus(
                project_id=project.id,
                provider_id=self.provider_id,
                status="error",
                summary="git status failed",
                warnings=[status_result.stderr.strip()],
            )

        lines = [line for line in status_result.stdout.splitlines() if line.strip()]
        changed = [line for line in lines if not line.startswith("##")]
        latest = _latest_commit(path)
        details: dict[str, Any] = {
            "path": str(path),
            "branch": branch,
            "changed_files": len(changed),
            "latest_commit": latest,
        }
        if changed:
            return ProjectStatus(
                project_id=project.id,
                provider_id=self.provider_id,
                status="dirty",
                summary=f"{len(changed)} changed file(s) on {branch}",
                next_actions=[{"label": "Review git status", "kind": "git-status"}],
                details=details,
            )

        return ProjectStatus(
            project_id=project.id,
            provider_id=self.provider_id,
            status="ok",
            summary=f"clean git worktree on {branch}",
            details=details,
        )

    def doctor(self, project: ProjectRef) -> ProjectStatus:
        return self.status(project)

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
        }


def _latest_commit(path: Path) -> str | None:
    result = _run(["git", "-C", str(path), "log", "-1", "--format=%h %cr %s"], cwd=None)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _run(args: list[str], cwd: Path | None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr=str(exc))
