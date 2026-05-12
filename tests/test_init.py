from __future__ import annotations

import tomllib

from typer.testing import CliRunner

from kansei.cli.main import app


def test_init_creates_private_instance_layout(tmp_path) -> None:
    target = tmp_path / "kansei-home"
    result = CliRunner().invoke(app, ["init", str(target), "--git", "--with-codex", "--with-mcp"])

    assert result.exit_code == 0, result.stdout
    for path in (
        "AGENTS.md",
        "KANSEI.md",
        "kansei.toml",
        "projects.toml",
        "providers.toml",
        ".gitignore",
        ".codex/config.toml",
        ".kansei/manifest.toml",
        ".kansei/lock.toml",
        "knowledge/profile.md",
        "dashboards/today.md",
        "runbooks/daily-planning.md",
        "prompts/codex-delegation.md",
    ):
        assert (target / path).exists(), path

    assert (target / ".git").exists()
    lock = tomllib.loads((target / ".kansei" / "lock.toml").read_text(encoding="utf-8"))
    locked_paths = {item["path"] for item in lock["managed_files"]}
    assert "AGENTS.md" in locked_paths
    assert ".codex/config.toml" in locked_paths


def test_init_refuses_non_empty_non_instance(tmp_path) -> None:
    target = tmp_path / "busy"
    target.mkdir()
    (target / "note.txt").write_text("already here", encoding="utf-8")

    result = CliRunner().invoke(app, ["init", str(target)])

    assert result.exit_code != 0
