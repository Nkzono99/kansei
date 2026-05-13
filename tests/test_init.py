from __future__ import annotations

import tomllib

from typer.testing import CliRunner

from kansei.cli.commands import init as init_command
from kansei.cli.main import app
from kansei.core.bootstrap import BootstrapResult


def test_init_creates_private_instance_layout(tmp_path) -> None:
    target = tmp_path / "kansei-home"
    result = CliRunner().invoke(
        app,
        [
            "init",
            str(target),
            "--git",
            "--with-codex",
            "--with-mcp",
            "--no-bootstrap",
            "--no-harnessops",
        ],
    )

    assert result.exit_code == 0, result.stdout
    for path in (
        "AGENTS.md",
        "KANSEI.md",
        "kansei.toml",
        "projects.toml",
        "providers.toml",
        ".gitignore",
        ".codex/config.toml",
        ".agents/skills/kansei-control-plane/SKILL.md",
        ".agents/skills/kansei-control-plane/scripts/check_instance.py",
        ".agents/skills/feedback-kansei/SKILL.md",
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
    assert ".agents/skills/kansei-control-plane/SKILL.md" in locked_paths
    assert ".agents/skills/feedback-kansei/SKILL.md" in locked_paths
    assert ".codex/config.toml" in locked_paths
    manifest = tomllib.loads((target / ".kansei" / "manifest.toml").read_text(encoding="utf-8"))
    assert manifest["cli"]["runner"] == "uvx"
    assert manifest["cli"]["command"] == "uvx --from kansei kansei"
    assert manifest["harness"]["kansei_version"] == "0.2.0"
    providers = tomllib.loads((target / "providers.toml").read_text(encoding="utf-8"))
    assert providers["providers"]["kansei"]["command"] == "uvx"
    assert providers["providers"]["kansei"]["args"] == ["--from", "kansei", "kansei"]
    assert "harnessops" in providers["providers"]


def test_init_refuses_non_empty_non_instance(tmp_path) -> None:
    target = tmp_path / "busy"
    target.mkdir()
    (target / "note.txt").write_text("already here", encoding="utf-8")

    result = CliRunner().invoke(app, ["init", str(target), "--no-bootstrap", "--no-harnessops"])

    assert result.exit_code != 0


def test_backup_and_migrate_commands(tmp_path) -> None:
    target = tmp_path / "kansei-home"
    init_result = CliRunner().invoke(
        app,
        ["init", str(target), "--with-mcp", "--no-bootstrap", "--no-harnessops"],
    )
    assert init_result.exit_code == 0

    backup_result = CliRunner().invoke(app, ["backup", "--root", str(target)])
    assert backup_result.exit_code == 0
    backup_path = target / ".kansei" / "backups"
    assert any(path.suffix == ".zip" for path in backup_path.iterdir())

    migrate_result = CliRunner().invoke(app, ["migrate", "--root", str(target), "--json"])
    assert migrate_result.exit_code == 0
    assert '"pending": []' in migrate_result.stdout


def test_init_uses_uvx_flow_by_default(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        init_command,
        "bootstrap_environment",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("bootstrap should not run")),
    )

    target = tmp_path / "kansei-home"
    result = CliRunner().invoke(app, ["init", str(target), "--no-harnessops"])

    assert result.exit_code == 0, result.stdout
    assert "Next: uvx --from kansei kansei doctor" in result.stdout
    assert not (target / ".venv").exists()


def test_init_can_bootstrap_legacy_local_venv(tmp_path, monkeypatch) -> None:
    calls: list[tuple[str, bool]] = []

    def fake_bootstrap(root, *, install_spec: str, required: bool):  # type: ignore[no-untyped-def]
        calls.append((install_spec, required))
        return BootstrapResult(
            created=(".venv", f"uv pip install {install_spec}"),
            skipped=(),
            warnings=(),
            activation_hint=".venv\\Scripts\\activate",
        )

    monkeypatch.setattr(init_command, "bootstrap_environment", fake_bootstrap)

    result = CliRunner().invoke(
        app,
        ["init", str(tmp_path / "kansei-home"), "--bootstrap", "--no-harnessops"],
    )

    assert result.exit_code == 0, result.stdout
    assert calls == [("kansei==0.2.0", False)]
    assert "Bootstrap: created .venv" in result.stdout
    assert "Bootstrap next: .venv\\Scripts\\activate" in result.stdout


def test_init_can_skip_bootstrap(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        init_command,
        "bootstrap_environment",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("bootstrap should not run")),
    )

    result = CliRunner().invoke(
        app,
        ["init", str(tmp_path / "kansei-home"), "--no-bootstrap", "--no-harnessops"],
    )

    assert result.exit_code == 0, result.stdout
