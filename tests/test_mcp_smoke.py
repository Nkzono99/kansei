from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from kansei.cli.main import app
from kansei.core.instance import init_instance
from kansei.mcp.config import inspect_mcp_config, plan_codex_config, write_codex_config
from kansei.mcp.server import FallbackMCP, KanseiMCPHandlers, build_server


def write_workspace(root: Path) -> None:
    (root / "kansei.toml").write_text(
        """
[safety]
remote_write_requires_explicit_approval = true
hpc_submit_requires_explicit_approval = true
""".strip(),
        encoding="utf-8",
    )
    (root / "projects.toml").write_text(
        """
schema_version = "0.1"

[[projects]]
id = "paper-demo"
name = "Paper Demo"
kind = "paper"
provider = "paperops"
location = "local"
path = "~/paper-demo"
priority = "A"
active = true

[[projects]]
id = "code-demo"
name = "Code Demo"
kind = "code"
provider = "generic-code"
location = "local"
path = "~/code-demo"
priority = "B"
active = false
""".strip(),
        encoding="utf-8",
    )
    (root / "providers.toml").write_text(
        """
schema_version = "0.1"

[providers.paperops]
type = "mcp"
mode = "stdio"
command = "pops"

[providers.generic-code]
type = "local"
mode = "cli"
command = "git"
""".strip(),
        encoding="utf-8",
    )
    knowledge = root / "knowledge"
    knowledge.mkdir()
    (knowledge / "hpc.md").write_text("HPC queue notes stay local.\n", encoding="utf-8")


def test_mcp_handlers_are_read_only(tmp_path: Path) -> None:
    write_workspace(tmp_path)
    handlers = KanseiMCPHandlers(tmp_path)

    assert handlers.health()["status"] == "ok"
    assert handlers.project_list(active=True)["projects"] == [
        {
            "id": "paper-demo",
            "name": "Paper Demo",
            "kind": "paper",
            "provider": "paperops",
            "location": "local",
            "priority": "A",
        }
    ]
    assert handlers.project_inspect("paper-demo")["policy"] == {
        "remote_write_requires_explicit_approval": True,
        "hpc_submit_requires_explicit_approval": True,
    }
    assert handlers.workspace_status()["active_project_count"] == 1
    assert handlers.knowledge_search("queue")["results"][0]["path"] == "knowledge/hpc.md"
    assert handlers.dashboard_plan_today()["writes_files"] is False


def test_build_server_registers_mvp_tools_and_resources(tmp_path: Path) -> None:
    write_workspace(tmp_path)
    server = build_server(workspace_root=tmp_path)

    if isinstance(server, FallbackMCP):
        assert {
            "kansei.health",
            "kansei.project.list",
            "kansei.project.inspect",
            "kansei.workspace.status",
            "kansei.knowledge.search",
            "kansei.dashboard.plan_today",
        }.issubset(server.tools)
        assert {
            "kansei://workspace/projects",
            "kansei://workspace/providers",
        }.issubset(server.resources)
        assert server.call_tool("kansei.health")["workspace_root"] == str(tmp_path)
        assert "paper-demo" in server.read_resource("kansei://workspace/projects")
    else:
        assert server is not None


def test_codex_mcp_config_is_generated_from_providers(tmp_path: Path) -> None:
    root = init_instance(tmp_path / "kansei", with_mcp=True)

    plan = plan_codex_config(root)

    assert "[mcp_servers.kansei]" in plan.content
    assert 'command = "uvx"' in plan.content
    for arg in ("--from", "kansei", "mcp", "serve", "--transport", "stdio"):
        assert f'"{arg}"' in plan.content
    assert "[mcp_servers.paperops]" in plan.content
    assert "[mcp_servers.runops_hpc]" in plan.content
    assert 'url = "http://127.0.0.1:18765/mcp"' in plan.content
    assert 'bearer_token_env_var = "RUNOPS_HPC_MCP_TOKEN"' in plan.content
    assert 'runops.job.submit' in plan.content

    path = write_codex_config(plan, force=True)
    assert path == root / ".codex" / "config.toml"
    assert inspect_mcp_config(root)["mcp_servers"]["runops_hpc"]["mode"] == "streamable-http"


def test_mcp_config_and_inspect_commands(tmp_path: Path) -> None:
    root = init_instance(tmp_path / "kansei", with_mcp=True)
    runner = CliRunner()

    preview = runner.invoke(app, ["mcp", "config", "--root", str(root)])
    assert preview.exit_code == 0
    assert "[mcp_servers.kansei]" in preview.stdout

    write = runner.invoke(app, ["mcp", "config", "--root", str(root), "--write", "--force"])
    assert write.exit_code == 0
    assert (root / ".codex" / "config.toml").exists()

    inspect = runner.invoke(app, ["mcp", "inspect", "--root", str(root)])
    assert inspect.exit_code == 0
    assert '"runops_hpc"' in inspect.stdout
