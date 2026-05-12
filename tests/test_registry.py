from __future__ import annotations

import pytest
from typer.testing import CliRunner

from kansei.cli.main import app
from kansei.core.errors import ProjectNotFoundError, RegistryError
from kansei.core.instance import init_instance
from kansei.registry.projects import Project, add_project, load_projects
from kansei.registry.providers import load_providers


def test_project_registry_load_filter_show_and_add(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "projects.toml").write_text(
        """
schema_version = "0.1"

[[projects]]
id = "kansei"
name = "Kansei"
kind = "management"
provider = "generic-code"
location = "local"
path = "."
priority = "A"
active = true

[[projects]]
id = "paper-demo"
name = "Paper Demo"
kind = "paper"
provider = "paperops"
location = "local"
path = "../paper"
priority = "B"
active = false
tags = ["writing"]
""",
        encoding="utf-8",
    )

    registry = load_projects(tmp_path)

    assert [project.id for project in registry.list(active=True)] == ["kansei"]
    assert registry.get("paper-demo").tags == ["writing"]

    add_project(
        Project(
            id="sim-demo",
            name="Simulation Demo",
            kind="experiment",
            provider="runops",
            location="ssh",
            host="hpc-login",
            path="/work/demo",
            priority="A",
        ),
        tmp_path,
    )

    updated = load_projects(tmp_path)
    assert updated.get("sim-demo").host == "hpc-login"
    assert [project.id for project in updated.list(priority="A")] == ["kansei", "sim-demo"]


def test_project_registry_rejects_duplicates_and_missing_projects(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "projects.toml").write_text(
        """
[[projects]]
id = "dup"
name = "One"
kind = "code"
provider = "generic-code"
location = "local"
path = "."

[[projects]]
id = "dup"
name = "Two"
kind = "code"
provider = "generic-code"
location = "local"
path = "."
""",
        encoding="utf-8",
    )

    with pytest.raises(RegistryError):
        load_projects(tmp_path)

    (tmp_path / "projects.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    with pytest.raises(ProjectNotFoundError):
        load_projects(tmp_path).get("missing")


def test_provider_registry_loads_and_normalizes_hyphenated_names(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "providers.toml").write_text(
        """
schema_version = "0.1"

[providers.generic_code]
type = "local"
mode = "cli"
command = "git"

[providers.runops_hpc]
type = "mcp"
mode = "streamable-http"
url = "http://127.0.0.1:18765/mcp"
required = false
""",
        encoding="utf-8",
    )

    registry = load_providers(tmp_path)

    assert registry.get("generic-code").command == "git"
    assert registry.get("runops_hpc").url == "http://127.0.0.1:18765/mcp"


def test_project_open_status_and_provider_connect_commands(tmp_path, monkeypatch) -> None:
    root = init_instance(tmp_path / "kansei", with_mcp=True)
    monkeypatch.chdir(root)

    open_result = CliRunner().invoke(app, ["project", "open", "kansei"])
    assert open_result.exit_code == 0
    assert str(root) in open_result.stdout

    status_result = CliRunner().invoke(app, ["project", "status", "kansei"])
    assert status_result.exit_code == 0
    assert '"project_id": "kansei"' in status_result.stdout

    connect_result = CliRunner().invoke(app, ["provider", "connect", "runops_hpc", "--tunnel"])
    assert connect_result.exit_code == 0
    assert "ssh -N -L 18765:127.0.0.1:18765 hpc-login" in connect_result.stdout
