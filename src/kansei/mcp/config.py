from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli_w

from kansei.core.lockfile import ManagedFile, load_lock, sha256_bytes, write_lock
from kansei.registry.providers import ProviderConfig, load_providers

CODEX_CONFIG_PATH = Path(".codex") / "config.toml"
CODEX_CONFIG_TEMPLATE = "generated/providers.toml"
DEFAULT_KANSEI_COMMAND = "uvx"
DEFAULT_KANSEI_ARGS = ["--from", "kansei", "kansei"]


@dataclass(frozen=True)
class CodexConfigPlan:
    root: Path
    content: str
    path: Path
    changed: bool
    exists: bool

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(self.root).as_posix()


def plan_codex_config(root: Path) -> CodexConfigPlan:
    path = root / CODEX_CONFIG_PATH
    content = render_codex_config(root)
    exists = path.exists()
    current = path.read_text(encoding="utf-8") if exists else None
    return CodexConfigPlan(
        root=root,
        content=content,
        path=path,
        changed=current != content,
        exists=exists,
    )


def render_codex_config(root: Path) -> str:
    providers = load_providers(root)
    data: dict[str, Any] = {
        "approval_policy": "on-request",
        "sandbox_mode": "workspace-write",
        "mcp_servers": {
            "kansei": {
                "command": _provider_command(
                    providers.providers.get("kansei"), DEFAULT_KANSEI_COMMAND
                ),
                "args": _kansei_mcp_args(providers.providers.get("kansei")),
                "cwd": ".",
                "startup_timeout_sec": 20,
                "tool_timeout_sec": 120,
                "enabled": True,
                "required": True,
            }
        },
    }

    for provider_id, provider in providers.providers.items():
        if provider_id == "kansei" or provider.type != "mcp":
            continue
        data["mcp_servers"][provider_id] = _mcp_server_config(provider_id, provider)

    return tomli_w.dumps(data)


def write_codex_config(plan: CodexConfigPlan, *, force: bool = False) -> Path:
    if plan.exists and plan.changed and not force:
        raise FileExistsError(
            f"{plan.relative_path} already exists and differs; rerun with --force to overwrite"
        )
    plan.path.parent.mkdir(parents=True, exist_ok=True)
    plan.path.write_bytes(plan.content.encode("utf-8"))
    _record_lock(plan)
    return plan.path


def inspect_mcp_config(root: Path) -> dict[str, Any]:
    providers = load_providers(root)
    plan = plan_codex_config(root)
    return {
        "root": str(root),
        "codex_config": {
            "path": plan.relative_path,
            "exists": plan.exists,
            "changed": plan.changed,
        },
        "provider_count": len(providers.providers),
        "mcp_servers": _server_summary(root),
    }


def _server_summary(root: Path) -> dict[str, dict[str, Any]]:
    providers = load_providers(root)
    servers = {
        "kansei": {
            "mode": "stdio",
            "required": True,
            "command": _provider_command(providers.providers.get("kansei"), DEFAULT_KANSEI_COMMAND),
            "args": _kansei_mcp_args(providers.providers.get("kansei")),
        }
    }
    for provider_id, provider in providers.providers.items():
        if provider_id == "kansei" or provider.type != "mcp":
            continue
        servers[provider_id] = {
            "mode": provider.mode,
            "required": provider.required,
            "command": provider.command,
            "url": provider.url,
            "token_env": provider.token_env,
            "ssh_tunnel": provider.ssh_tunnel,
        }
    return servers


def _mcp_server_config(provider_id: str, provider: ProviderConfig) -> dict[str, Any]:
    base: dict[str, Any] = {
        "startup_timeout_sec": 20,
        "tool_timeout_sec": 180 if "runops" in provider_id else 120,
        "enabled": True,
        "required": provider.required,
    }
    if provider.mode == "stdio":
        base["command"] = provider.command
        if provider.args:
            base["args"] = provider.args
    else:
        base["url"] = provider.url
        if provider.token_env:
            base["bearer_token_env_var"] = provider.token_env
    if "runops" in provider_id:
        base["enabled_tools"] = [
            "runops.health",
            "runops.project.status",
            "runops.run.list",
            "runops.run.inspect",
            "runops.run.logs",
            "runops.slurm.queue",
            "runops.job.plan_submit",
        ]
        base["disabled_tools"] = [
            "runops.job.submit",
            "runops.job.cancel",
            "runops.run.delete",
            "runops.fs.delete",
        ]
    return base


def _provider_command(provider: ProviderConfig | None, default: str) -> str:
    if provider and provider.command:
        return provider.command
    return default


def _kansei_mcp_args(provider: ProviderConfig | None) -> list[str]:
    if provider and provider.args:
        prefix = list(provider.args)
    elif provider and provider.command and provider.command != DEFAULT_KANSEI_COMMAND:
        prefix = []
    else:
        prefix = list(DEFAULT_KANSEI_ARGS)
    return [*prefix, "mcp", "serve", "--transport", "stdio"]


def _record_lock(plan: CodexConfigPlan) -> None:
    lock = load_lock(plan.root)
    lock[plan.relative_path] = ManagedFile(
        path=plan.relative_path,
        template=CODEX_CONFIG_TEMPLATE,
        version="0.1.0",
        checksum=sha256_bytes(plan.content.encode("utf-8")),
        file_class="generated",
    )
    write_lock(plan.root, lock)
