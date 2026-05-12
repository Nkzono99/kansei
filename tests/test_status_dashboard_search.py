from __future__ import annotations

import subprocess
from datetime import date

from kansei.dashboard.generator import workspace_status
from kansei.dashboard.renderer import render_today, render_weekly, write_today
from kansei.knowledge.search import search_knowledge


def test_workspace_status_uses_generic_code_git_status(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "providers.toml").write_text(
        """
[providers.generic_code]
type = "local"
mode = "cli"
command = "git"
""",
        encoding="utf-8",
    )
    project_dir = tmp_path / "app"
    project_dir.mkdir()
    subprocess.run(["git", "init"], cwd=project_dir, check=True, stdout=subprocess.PIPE)
    (project_dir / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "projects.toml").write_text(
        """
[[projects]]
id = "app"
name = "App"
kind = "code"
provider = "generic-code"
location = "local"
path = "app"
priority = "A"
active = true
""",
        encoding="utf-8",
    )

    status = workspace_status(tmp_path)

    assert status.status == "dirty"
    assert status.projects[0].project_id == "app"
    assert status.projects[0].details["changed_files"] == 1


def test_today_dashboard_preview_and_write(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "providers.toml").write_text(
        """
[providers.generic_code]
type = "local"
mode = "cli"
command = "git"
""",
        encoding="utf-8",
    )
    (tmp_path / "projects.toml").write_text(
        """
[[projects]]
id = "paper-demo"
name = "Paper Demo"
kind = "paper"
provider = "generic-code"
location = "local"
path = "missing"
priority = "A"
active = true
""",
        encoding="utf-8",
    )

    rendered = render_today(tmp_path, today=date(2026, 5, 12))

    assert "# Today - 2026-05-12" in rendered
    assert "| Paper Demo | generic-code | error | Review next step |" in rendered
    assert not (tmp_path / "dashboards" / "today.md").exists()

    path = write_today(tmp_path, today=date(2026, 5, 12))
    assert path == tmp_path / "dashboards" / "today.md"
    assert path.read_text(encoding="utf-8") == rendered


def test_weekly_dashboard_preview(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "providers.toml").write_text(
        """
[providers.generic_code]
type = "local"
mode = "cli"
command = "git"
""",
        encoding="utf-8",
    )
    (tmp_path / "projects.toml").write_text(
        """
[[projects]]
id = "kansei"
name = "Kansei"
kind = "management"
provider = "generic-code"
location = "local"
path = "."
priority = "A"
active = true
""",
        encoding="utf-8",
    )

    rendered = render_weekly(tmp_path, today=date(2026, 5, 12))

    assert "# Weekly - 2026-05-12" in rendered
    assert "Kansei (A)" in rendered


def test_knowledge_search_is_scoped_to_local_knowledge_surfaces(tmp_path) -> None:
    (tmp_path / "kansei.toml").write_text('schema_version = "0.1"\n', encoding="utf-8")
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "runbooks").mkdir()
    (tmp_path / "prompts").mkdir()
    (tmp_path / "dashboards").mkdir()
    (tmp_path / "external-project").mkdir()
    (tmp_path / "knowledge" / "hpc.md").write_text("HPC queue notes\n", encoding="utf-8")
    (tmp_path / "runbooks" / "daily.md").write_text("Daily planning\n", encoding="utf-8")
    (tmp_path / "KANSEI.md").write_text("Kansei control plane\n", encoding="utf-8")
    (tmp_path / "external-project" / "secret.md").write_text(
        "HPC secret should not be searched\n",
        encoding="utf-8",
    )

    results = search_knowledge("hpc", tmp_path)

    assert [(hit.path, hit.line) for hit in results.hits] == [("knowledge/hpc.md", 1)]
