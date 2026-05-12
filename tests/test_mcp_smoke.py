from __future__ import annotations

from pathlib import Path

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
