from __future__ import annotations

import datetime as dt
import json
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kansei import __version__

FastMCPClass: Any = None
try:  # pragma: no cover - exercised only when the optional MCP SDK is installed.
    from mcp.server.fastmcp import FastMCP as _FastMCPClass

    FastMCPClass = _FastMCPClass
except ImportError:  # pragma: no cover - behavior is covered via fallback tests.
    pass

DEFAULT_POLICY = {
    "remote_write_requires_explicit_approval": True,
    "hpc_submit_requires_explicit_approval": True,
}


class FallbackMCP:
    """Tiny test double used when mcp.server.fastmcp is not installed."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, Callable[..., Any]] = {}
        self.resources: dict[str, Callable[[], str]] = {}

    def tool(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[name] = func
            return func

        return decorator

    def resource(self, uri: str) -> Callable[[Callable[[], str]], Callable[[], str]]:
        def decorator(func: Callable[[], str]) -> Callable[[], str]:
            self.resources[uri] = func
            return func

        return decorator

    def call_tool(self, name: str, **kwargs: Any) -> Any:
        return self.tools[name](**kwargs)

    def read_resource(self, uri: str) -> str:
        return self.resources[uri]()

    def run(self, *_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("mcp.server.fastmcp is not installed")


@dataclass(frozen=True)
class KanseiMCPHandlers:
    workspace_root: Path | None = None

    def root(self) -> Path:
        return find_workspace_root(self.workspace_root)

    def health(self) -> dict[str, Any]:
        root = self.root()
        warnings = []
        if not (root / "projects.toml").exists():
            warnings.append("projects.toml not found")
        if not (root / "providers.toml").exists():
            warnings.append("providers.toml not found")
        return {
            "provider": "kansei",
            "status": "ok" if not warnings else "warning",
            "version": __version__,
            "workspace_root": str(root),
            "warnings": warnings,
        }

    def project_list(
        self,
        active: bool | None = None,
        kind: str | None = None,
        priority: str | None = None,
    ) -> dict[str, Any]:
        projects = load_projects(self.root())
        filtered = [
            project_summary(project)
            for project in projects
            if _matches_project(project, active=active, kind=kind, priority=priority)
        ]
        return {"projects": filtered}

    def project_inspect(self, project_id: str) -> dict[str, Any]:
        projects = load_projects(self.root())
        for project in projects:
            if project.get("id") == project_id:
                return {
                    "project": project,
                    "policy": load_safety_policy(self.root()),
                }
        return {
            "error": "project_not_found",
            "project_id": project_id,
        }

    def workspace_status(self) -> dict[str, Any]:
        root = self.root()
        projects = load_projects(root)
        providers = load_providers(root)
        active_projects = [p for p in projects if p.get("active", True)]
        warnings = []
        missing_providers = sorted(
            {
                str(project.get("provider"))
                for project in projects
                if project.get("provider") and str(project.get("provider")) not in providers
            }
        )
        if missing_providers:
            warnings.append(f"missing provider definitions: {', '.join(missing_providers)}")
        return {
            "workspace_root": str(root),
            "status": "ok" if not warnings else "warning",
            "project_count": len(projects),
            "active_project_count": len(active_projects),
            "provider_count": len(providers),
            "warnings": warnings,
            "projects": [project_summary(project) for project in active_projects],
        }

    def knowledge_search(self, query: str, max_results: int = 10) -> dict[str, Any]:
        root = self.root()
        normalized = query.casefold()
        results = []
        if not normalized:
            return {"query": query, "results": []}

        for path in iter_searchable_files(root):
            text = safe_read_text(path)
            if not text:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                if normalized in line.casefold():
                    results.append(
                        {
                            "path": path.relative_to(root).as_posix(),
                            "line": line_no,
                            "snippet": line.strip(),
                        }
                    )
                    break
            if len(results) >= max_results:
                break
        return {"query": query, "results": results}

    def dashboard_plan_today(self) -> dict[str, Any]:
        root = self.root()
        projects = load_projects(root)
        active = [p for p in projects if p.get("active", True)]
        today = dt.date.today().isoformat()
        focus = [p for p in active if p.get("priority") == "A"][:3]
        lines = [
            f"# Today - {today}",
            "",
            "## Focus",
            *[f"- [ ] {p.get('name', p.get('id'))}" for p in focus],
            "",
            "## Active projects",
            "| project | provider | priority | next action |",
            "|---|---|---|---|",
        ]
        for project in active:
            lines.append(
                "| {name} | {provider} | {priority} | inspect provider status |".format(
                    name=project.get("name", project.get("id", "")),
                    provider=project.get("provider", ""),
                    priority=project.get("priority", ""),
                )
            )
        return {
            "workspace_root": str(root),
            "date": today,
            "writes_files": False,
            "plan_markdown": "\n".join(lines),
        }

    def workspace_projects_resource(self) -> str:
        return resource_text(self.root() / "projects.toml")

    def workspace_providers_resource(self) -> str:
        return resource_text(self.root() / "providers.toml")


def build_server(workspace_root: str | Path | None = None) -> Any:
    handlers = KanseiMCPHandlers(Path(workspace_root) if workspace_root is not None else None)
    server = FastMCPClass("Kansei") if FastMCPClass is not None else FallbackMCP("Kansei")

    @server.tool(name="kansei.health")  # type: ignore[untyped-decorator]
    def health() -> dict[str, Any]:
        return handlers.health()

    @server.tool(name="kansei.project.list")  # type: ignore[untyped-decorator]
    def project_list(
        active: bool | None = None,
        kind: str | None = None,
        priority: str | None = None,
    ) -> dict[str, Any]:
        return handlers.project_list(active=active, kind=kind, priority=priority)

    @server.tool(name="kansei.project.inspect")  # type: ignore[untyped-decorator]
    def project_inspect(project_id: str) -> dict[str, Any]:
        return handlers.project_inspect(project_id)

    @server.tool(name="kansei.workspace.status")  # type: ignore[untyped-decorator]
    def workspace_status() -> dict[str, Any]:
        return handlers.workspace_status()

    @server.tool(name="kansei.knowledge.search")  # type: ignore[untyped-decorator]
    def knowledge_search(query: str, max_results: int = 10) -> dict[str, Any]:
        return handlers.knowledge_search(query=query, max_results=max_results)

    @server.tool(name="kansei.dashboard.plan_today")  # type: ignore[untyped-decorator]
    def dashboard_plan_today() -> dict[str, Any]:
        return handlers.dashboard_plan_today()

    @server.resource("kansei://workspace/projects")  # type: ignore[untyped-decorator]
    def workspace_projects() -> str:
        return handlers.workspace_projects_resource()

    @server.resource("kansei://workspace/providers")  # type: ignore[untyped-decorator]
    def workspace_providers() -> str:
        return handlers.workspace_providers_resource()

    return server


def run(
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 18764,
    workspace_root: str | Path | None = None,
) -> None:
    server = build_server(workspace_root=workspace_root)
    if transport == "stdio":
        server.run(transport="stdio")
        return
    if transport == "streamable-http":
        try:
            server.run(transport="streamable-http", host=host, port=port)
        except TypeError:
            server.run(transport="streamable-http")
        return
    raise ValueError(f"unsupported transport: {transport}")


def find_workspace_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for path in [current, *current.parents]:
        if (path / "kansei.toml").exists() or (path / "projects.toml").exists():
            return path
    return current


def load_projects(root: Path) -> list[dict[str, Any]]:
    data = load_toml(root / "projects.toml")
    projects = data.get("projects", [])
    if not isinstance(projects, list):
        return []
    return [project for project in projects if isinstance(project, dict)]


def load_providers(root: Path) -> dict[str, Any]:
    data = load_toml(root / "providers.toml")
    providers = data.get("providers", {})
    return providers if isinstance(providers, dict) else {}


def load_safety_policy(root: Path) -> dict[str, bool]:
    data = load_toml(root / "kansei.toml")
    safety = data.get("safety", {})
    policy = dict(DEFAULT_POLICY)
    if isinstance(safety, dict):
        for key in DEFAULT_POLICY:
            if isinstance(safety.get(key), bool):
                policy[key] = safety[key]
    return policy


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def project_summary(project: dict[str, Any]) -> dict[str, Any]:
    return {
        key: project[key]
        for key in ("id", "name", "kind", "provider", "location", "priority")
        if key in project
    }


def _matches_project(
    project: dict[str, Any],
    active: bool | None,
    kind: str | None,
    priority: str | None,
) -> bool:
    if active is not None and bool(project.get("active", True)) != active:
        return False
    if kind is not None and project.get("kind") != kind:
        return False
    return priority is None or project.get("priority") == priority


def iter_searchable_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for name in ("knowledge", "runbooks", "prompts", "dashboards"):
        directory = root / name
        if directory.exists():
            candidates.extend(path for path in directory.rglob("*.md") if path.is_file())
    for name in ("KANSEI.md",):
        path = root / name
        if path.exists():
            candidates.append(path)
    return sorted(candidates)


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def resource_text(path: Path) -> str:
    if not path.exists():
        return json.dumps({"error": "not_found", "path": path.name})
    return safe_read_text(path)
