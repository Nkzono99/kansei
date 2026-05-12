from __future__ import annotations

from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

StatusValue = Literal["ok", "dirty", "warning", "error", "unknown", "skipped"]


class ProjectRef(BaseModel):
    id: str
    name: str
    kind: str
    provider: str
    location: str
    path: str
    host: str | None = None
    priority: str = "C"
    active: bool = True
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None


class ProviderHealth(BaseModel):
    provider_id: str
    status: StatusValue = "unknown"
    summary: str = ""
    warnings: list[str] = Field(default_factory=list)


class ProjectStatus(BaseModel):
    project_id: str
    provider_id: str
    status: StatusValue = "unknown"
    summary: str
    warnings: list[str] = Field(default_factory=list)
    next_actions: list[dict[str, Any]] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class WorkspaceStatus(BaseModel):
    status: StatusValue
    summary: str
    projects: list[ProjectStatus] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ProviderAdapter(Protocol):
    provider_id: str

    def health(self) -> ProviderHealth: ...

    def status(self, project: ProjectRef) -> ProjectStatus: ...

    def doctor(self, project: ProjectRef) -> ProjectStatus: ...

    def delegate_plan(self, project: ProjectRef, task: str) -> dict[str, Any]: ...
