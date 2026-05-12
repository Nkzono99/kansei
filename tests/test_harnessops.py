from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kansei.cli.commands import init as init_command
from kansei.cli.commands import update as update_command
from kansei.cli.main import app
from kansei.core import harnessops
from kansei.core.harnessops import (
    HarnessOpsUnavailable,
    run_harnessops_init,
    run_harnessops_update,
)
from kansei.core.instance import init_instance


def test_harnessops_init_skips_when_hops_is_unavailable(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(harnessops, "_resolve_hops_command", lambda: None)

    results = run_harnessops_init(tmp_path)

    assert results[0].status == "skipped"
    assert "hops command not found" in results[0].reason


def test_harnessops_init_can_require_hops(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(harnessops, "_resolve_hops_command", lambda: None)

    with pytest.raises(HarnessOpsUnavailable):
        run_harnessops_init(tmp_path, required=True)


def test_harnessops_update_dry_run_initializes_without_writing(tmp_path, monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], Path]] = []
    _fake_hops(monkeypatch, calls)

    results = run_harnessops_update(tmp_path, apply=False)

    assert results[0].ran
    assert calls == [(("hops", "init", "--profile", "generic-code", "--dry-run"), tmp_path)]


def test_harnessops_update_apply_initializes_then_updates(tmp_path, monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], Path]] = []
    _fake_hops(monkeypatch, calls)

    results = run_harnessops_update(tmp_path, apply=True, with_agent_bridge=True)

    assert [result.ran for result in results] == [True, True]
    assert calls == [
        (("hops", "init", "--profile", "generic-code", "--with-agent-bridge"), tmp_path),
        (("hops", "update-harness", "--agent-bridge", "--codex"), tmp_path),
    ]


def test_harnessops_update_existing_instance_runs_update_only(tmp_path, monkeypatch) -> None:
    (tmp_path / ".harnessops").mkdir()
    (tmp_path / ".harnessops" / "project.toml").write_text("schema_version = '0.1'\n")
    calls: list[tuple[tuple[str, ...], Path]] = []
    _fake_hops(monkeypatch, calls)

    run_harnessops_update(tmp_path, apply=False)

    assert calls == [(("hops", "update-harness", "--dry-run"), tmp_path)]


def test_init_command_chains_harnessops(tmp_path, monkeypatch) -> None:
    calls: list[tuple[Path, str, bool, bool]] = []

    def fake_init(
        root: Path,
        *,
        profile: str,
        with_agent_bridge: bool,
        required: bool,
    ) -> list[harnessops.HarnessOpsResult]:
        calls.append((root, profile, with_agent_bridge, required))
        return [harnessops.HarnessOpsResult(status="ran", args=("init", "--profile", profile))]

    monkeypatch.setattr(init_command, "run_harnessops_init", fake_init)
    monkeypatch.setattr(init_command, "hops_is_available", lambda: True)

    result = CliRunner().invoke(
        app,
        [
            "init",
            str(tmp_path / "kansei-home"),
            "--harnessops-profile",
            "python-package",
            "--with-harnessops-agent-bridge",
            "--require-harnessops",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert calls == [(tmp_path / "kansei-home", "python-package", True, True)]
    assert "HarnessOps: ran hops init --profile python-package" in result.stdout


def test_init_command_require_harnessops_preflights_before_writing(tmp_path, monkeypatch) -> None:
    target = tmp_path / "kansei-home"
    monkeypatch.setattr(init_command, "hops_is_available", lambda: False)

    result = CliRunner().invoke(app, ["init", str(target), "--require-harnessops"])

    assert result.exit_code == 1
    assert not target.exists()
    assert "hops command not found" in result.stderr


def test_init_command_can_skip_harnessops(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        init_command,
        "run_harnessops_init",
        lambda *args, **kwargs: pytest.fail("hops should not run"),
    )

    result = CliRunner().invoke(app, ["init", str(tmp_path / "kansei-home"), "--no-harnessops"])

    assert result.exit_code == 0, result.stdout


def test_update_command_chains_harnessops_when_kansei_is_current(
    tmp_path, monkeypatch
) -> None:
    root = init_instance(tmp_path / "kansei-home")
    calls: list[tuple[Path, bool, str, bool, bool]] = []

    def fake_update(
        root: Path,
        *,
        apply: bool,
        profile: str,
        with_agent_bridge: bool,
        required: bool,
    ) -> list[harnessops.HarnessOpsResult]:
        calls.append((root, apply, profile, with_agent_bridge, required))
        return [harnessops.HarnessOpsResult(status="ran", args=("update-harness", "--dry-run"))]

    monkeypatch.setattr(update_command, "run_harnessops_update", fake_update)

    result = CliRunner().invoke(app, ["update-harness", "--root", str(root)])

    assert result.exit_code == 0, result.stdout
    assert "Kansei harness is up to date." in result.stdout
    assert calls == [(root, False, "generic-code", False, False)]
    assert "HarnessOps: ran hops update-harness --dry-run" in result.stdout


def test_update_command_can_skip_harnessops(tmp_path, monkeypatch) -> None:
    root = init_instance(tmp_path / "kansei-home")
    monkeypatch.setattr(
        update_command,
        "run_harnessops_update",
        lambda *args, **kwargs: pytest.fail("hops should not run"),
    )

    result = CliRunner().invoke(app, ["update-harness", "--root", str(root), "--no-harnessops"])

    assert result.exit_code == 0, result.stdout


def test_update_command_require_harnessops_preflights_before_apply(
    tmp_path, monkeypatch
) -> None:
    root = init_instance(tmp_path / "kansei-home")
    (root / "KANSEI.md").unlink()
    monkeypatch.setattr(update_command, "hops_is_available", lambda: False)

    result = CliRunner().invoke(
        app,
        ["update-harness", "--root", str(root), "--apply", "--require-harnessops"],
    )

    assert result.exit_code == 1
    assert not (root / "KANSEI.md").exists()
    assert "hops command not found" in result.stderr


def _fake_hops(monkeypatch, calls: list[tuple[tuple[str, ...], Path]]) -> None:
    monkeypatch.setattr(harnessops, "_resolve_hops_command", lambda: ("hops",))

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        text: bool,
        capture_output: bool,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        assert text
        assert capture_output
        assert not check
        calls.append((tuple(command), cwd))
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(harnessops.subprocess, "run", fake_run)
