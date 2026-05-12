from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from kansei.core.config import load_toml
from kansei.core.errors import ProviderNotFoundError, RegistryError
from kansei.core.paths import find_instance_root

ProviderType = Literal["local", "mcp", "ssh", "external"]


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: ProviderType
    mode: str
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    url: str | None = None
    ssh_tunnel: str | None = None
    token_env: str | None = None
    required: bool = False

    @model_validator(mode="after")
    def command_or_url_required(self) -> ProviderConfig:
        if self.type in {"local", "ssh"} and not self.command:
            raise ValueError("command is required for local/ssh providers")
        if self.type == "mcp" and self.mode != "stdio" and not self.url:
            raise ValueError("url is required for non-stdio mcp providers")
        if self.type == "mcp" and self.mode == "stdio" and not self.command:
            raise ValueError("command is required for stdio mcp providers")
        return self


class ProviderRegistry(BaseModel):
    schema_version: str = "0.1"
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)

    def list(self, *, required: bool | None = None) -> dict[str, ProviderConfig]:
        if required is None:
            return dict(self.providers)
        return {
            provider_id: provider
            for provider_id, provider in self.providers.items()
            if provider.required is required
        }

    def get(self, provider_id: str) -> ProviderConfig:
        normalized = provider_id.replace("-", "_")
        for key in (provider_id, normalized):
            if key in self.providers:
                return self.providers[key]
        raise ProviderNotFoundError(f"unknown provider: {provider_id}")


def load_providers(root: Path | str | None = None) -> ProviderRegistry:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    path = instance_root / "providers.toml"
    data = load_toml(path) if path.exists() else {"schema_version": "0.1", "providers": {}}
    try:
        return ProviderRegistry.model_validate(data)
    except ValueError as exc:
        raise RegistryError(f"invalid providers registry: {exc}") from exc
