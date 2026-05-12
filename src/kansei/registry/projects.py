from __future__ import annotations

import builtins
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from kansei.core.config import load_toml
from kansei.core.errors import ProjectNotFoundError, RegistryError
from kansei.core.paths import find_instance_root

ProjectKind = Literal["management", "paper", "experiment", "code", "reading", "admin", "other"]
ProjectLocation = Literal["local", "ssh", "cloud", "external"]
ProjectPriority = Literal["A", "B", "C", "hold"]


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    kind: ProjectKind
    provider: str
    location: ProjectLocation
    path: str
    host: str | None = None
    priority: ProjectPriority = "C"
    active: bool = True
    codex_profile: str | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("id", "name", "provider", "path")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value.strip()

    @model_validator(mode="after")
    def ssh_requires_host(self) -> Project:
        if self.location == "ssh" and not self.host:
            raise ValueError("host is required when location is ssh")
        return self


class ProjectRegistry(BaseModel):
    schema_version: str = "0.1"
    projects: builtins.list[Project] = Field(default_factory=list)

    @model_validator(mode="after")
    def project_ids_are_unique(self) -> ProjectRegistry:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for project in self.projects:
            if project.id in seen:
                duplicates.add(project.id)
            seen.add(project.id)
        if duplicates:
            joined = ", ".join(sorted(duplicates))
            raise ValueError(f"duplicate project id(s): {joined}")
        return self

    def list(
        self,
        *,
        active: bool | None = None,
        kind: str | None = None,
        priority: str | None = None,
        provider: str | None = None,
        tag: str | None = None,
    ) -> builtins.list[Project]:
        projects = self.projects
        if active is not None:
            projects = [project for project in projects if project.active is active]
        if kind is not None:
            projects = [project for project in projects if project.kind == kind]
        if priority is not None:
            projects = [project for project in projects if project.priority == priority]
        if provider is not None:
            projects = [project for project in projects if project.provider == provider]
        if tag is not None:
            projects = [project for project in projects if tag in project.tags]
        return projects

    def get(self, project_id: str) -> Project:
        for project in self.projects:
            if project.id == project_id:
                return project
        raise ProjectNotFoundError(f"unknown project: {project_id}")

    def add(self, project: Project) -> ProjectRegistry:
        if any(existing.id == project.id for existing in self.projects):
            raise RegistryError(f"project already exists: {project.id}")
        return self.model_copy(update={"projects": [*self.projects, project]})


def load_projects(root: Path | str | None = None) -> ProjectRegistry:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    path = instance_root / "projects.toml"
    data = load_toml(path) if path.exists() else {"schema_version": "0.1", "projects": []}
    try:
        return ProjectRegistry.model_validate(data)
    except ValueError as exc:
        raise RegistryError(f"invalid projects registry: {exc}") from exc


def dump_projects(registry: ProjectRegistry) -> str:
    lines = [f'schema_version = "{registry.schema_version}"', ""]
    for project in registry.projects:
        data = project.model_dump(exclude_none=True)
        lines.append("[[projects]]")
        for key, value in data.items():
            lines.append(_toml_line(key, value))
        lines.append("")
    return "\n".join(lines)


def save_projects(registry: ProjectRegistry, root: Path | str | None = None) -> Path:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    path = instance_root / "projects.toml"
    path.write_text(dump_projects(registry), encoding="utf-8")
    return path


def add_project(project: Project, root: Path | str | None = None) -> ProjectRegistry:
    registry = load_projects(root)
    updated = registry.add(project)
    save_projects(updated, root)
    return updated


def _toml_line(key: str, value: object) -> str:
    if isinstance(value, bool):
        return f"{key} = {str(value).lower()}"
    if isinstance(value, list):
        items = ", ".join(_toml_value(item) for item in value)
        return f"{key} = [{items}]"
    return f"{key} = {_toml_value(value)}"


def _toml_value(value: object) -> str:
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
