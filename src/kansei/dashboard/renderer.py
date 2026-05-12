from __future__ import annotations

from datetime import date
from pathlib import Path

from kansei.core.paths import find_instance_root
from kansei.dashboard.generator import workspace_status
from kansei.providers.base import ProjectStatus, WorkspaceStatus
from kansei.registry.projects import load_projects


def render_today(root: Path | str | None = None, *, today: date | None = None) -> str:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    current_date = today or date.today()
    status = workspace_status(instance_root)
    projects = load_projects(instance_root).list(active=True)

    lines = [
        f"# Today - {current_date.isoformat()}",
        "",
        "## 1. Focus",
        "",
        *focus_lines(status),
        "",
        "## 2. A-priority projects",
        "",
        "| project | provider | status | next action |",
        "|---|---|---|---|",
    ]

    by_id = {item.project_id: item for item in status.projects}
    for project in [project for project in projects if project.priority == "A"]:
        project_status = by_id.get(project.id)
        status_label = project_status.status if project_status else "unknown"
        next_action = _next_action(project_status)
        lines.append(f"| {project.name} | {project.provider} | {status_label} | {next_action} |")

    lines.extend(["", "## 3. HPC", ""])
    lines.extend(_section_lines(status, kinds={"experiment"}))
    lines.extend(["", "## 4. Papers", ""])
    lines.extend(_section_lines(status, kinds={"paper"}))
    lines.extend(["", "## 5. Code", ""])
    lines.extend(_section_lines(status, kinds={"code", "management"}))
    lines.extend(["", "## 6. Decisions needed", ""])
    lines.extend(_decision_lines(status))
    lines.extend(["", "## 7. Deferred / holding", ""])
    hold_projects = [
        project for project in projects if project.priority == "hold" or not project.active
    ]
    lines.extend([f"- {project.name}" for project in hold_projects] or ["- None"])
    lines.extend(["", "## 8. Notes", "", "- "])
    return "\n".join(lines).rstrip() + "\n"


def write_today(root: Path | str | None = None, *, today: date | None = None) -> Path:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    path = instance_root / "dashboards" / "today.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_today(instance_root, today=today), encoding="utf-8")
    return path


def focus_lines(status: WorkspaceStatus) -> list[str]:
    attention = [
        item for item in status.projects if item.status in {"error", "dirty", "warning", "skipped"}
    ][:3]
    if not attention:
        return ["- [ ] Pick one A-priority project and define the next concrete action."]
    return [f"- [ ] {item.project_id}: {item.summary}" for item in attention]


def _section_lines(status: WorkspaceStatus, *, kinds: set[str]) -> list[str]:
    lines = [
        f"- {item.project_id}: {item.summary}"
        for item in status.projects
        if str(item.details.get("kind", "")) in kinds
    ]
    if lines:
        return lines
    fallback = [
        f"- {item.project_id}: {item.summary}"
        for item in status.projects
        if _matches(item, kinds)
    ]
    return fallback or ["- None"]


def _matches(status: ProjectStatus, kinds: set[str]) -> bool:
    project_id = status.project_id.lower()
    if "paper" in kinds:
        return "paper" in project_id
    if "experiment" in kinds:
        return "sim" in project_id or "hpc" in project_id
    if "code" in kinds or "management" in kinds:
        return status.provider_id in {"generic-code", "kansei", "harnessops"}
    return False


def _decision_lines(status: WorkspaceStatus) -> list[str]:
    items = [
        f"- {item.project_id}: {warning}"
        for item in status.projects
        for warning in item.warnings[:1]
    ]
    items.extend(f"- Workspace: {warning}" for warning in status.warnings)
    return items or ["- None"]


def _next_action(status: ProjectStatus | None) -> str:
    if status is None or not status.next_actions:
        return "Review next step"
    return str(status.next_actions[0].get("label", "Review next step"))
