from __future__ import annotations

from pathlib import Path

from kansei.core.paths import find_instance_root, resolve_instance_path
from kansei.providers.base import ProjectRef, ProjectStatus, StatusValue, WorkspaceStatus
from kansei.registry.discovery import get_builtin_provider
from kansei.registry.projects import Project, load_projects
from kansei.registry.providers import load_providers


def workspace_status(
    root: Path | str | None = None,
    *,
    active: bool | None = True,
    kind: str | None = None,
    priority: str | None = None,
) -> WorkspaceStatus:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    projects = load_projects(instance_root).list(active=active, kind=kind, priority=priority)
    provider_registry = load_providers(instance_root)
    statuses: list[ProjectStatus] = []
    warnings: list[str] = []

    for project in projects:
        try:
            provider_registry.get(project.provider)
        except Exception as exc:
            warnings.append(f"{project.id}: {exc}")
        adapter = get_builtin_provider(project.provider)
        status = adapter.status(_project_ref(project, instance_root))
        status.details.setdefault("kind", project.kind)
        status.details.setdefault("priority", project.priority)
        statuses.append(status)

    error_count = sum(1 for status in statuses if status.status == "error")
    dirty_count = sum(1 for status in statuses if status.status == "dirty")
    warning_count = sum(1 for status in statuses if status.status in {"warning", "skipped"})

    if error_count:
        status_value: StatusValue = "error"
    elif dirty_count:
        status_value = "dirty"
    elif warning_count or warnings:
        status_value = "warning"
    else:
        status_value = "ok"

    summary = (
        f"{len(statuses)} active project(s): "
        f"{error_count} error, {dirty_count} dirty, {warning_count} warning/skipped"
    )
    return WorkspaceStatus(
        status=status_value,
        summary=summary,
        projects=statuses,
        warnings=warnings,
    )


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
