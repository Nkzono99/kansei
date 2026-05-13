from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from kansei.cli.commands import update as update_command
from kansei.cli.main import app
from kansei.core.instance import init_instance
from kansei.update.chain import (
    UpgradeChainError,
    build_upgrade_chain,
    run_upgrade_chain,
    upgrade_step_command,
)


def test_upgrade_chain_uses_latest_patch_per_minor(tmp_path: Path) -> None:
    root = init_instance(tmp_path / "kansei")

    chain = build_upgrade_chain(
        root,
        current_version="0.4.2",
        applied_version="0.1.7",
        fetch_versions=lambda: ("0.2.0", "0.2.5", "0.3.1", "0.3.4", "0.4.2"),
    )

    assert [(step.from_version, step.to_version) for step in chain.steps] == [
        ("0.1.7", "0.2.5"),
        ("0.2.5", "0.3.4"),
        ("0.3.4", "0.4.2"),
    ]


def test_upgrade_chain_can_target_minor_checkpoint(tmp_path: Path) -> None:
    root = init_instance(tmp_path / "kansei")

    chain = build_upgrade_chain(
        root,
        target="0.3",
        current_version="0.4.2",
        applied_version="0.1.7",
        fetch_versions=lambda: ("0.2.5", "0.3.1", "0.3.4", "0.4.2"),
    )

    assert chain.target_version == "0.3.4"
    assert [step.to_version for step in chain.steps] == ["0.2.5", "0.3.4"]


def test_apply_chain_requires_major_confirmation(tmp_path: Path) -> None:
    root = init_instance(tmp_path / "kansei")
    chain = build_upgrade_chain(
        root,
        current_version="1.0.0",
        applied_version="0.9.0",
        fetch_versions=lambda: ("1.0.0",),
    )

    with pytest.raises(UpgradeChainError):
        run_upgrade_chain(chain)


def test_apply_chain_runs_exact_uvx_steps(tmp_path: Path, monkeypatch) -> None:
    root = init_instance(tmp_path / "kansei")
    chain = build_upgrade_chain(
        root,
        current_version="0.3.0",
        applied_version="0.1.0",
        fetch_versions=lambda: ("0.2.1", "0.3.0"),
    )
    calls: list[tuple[str, ...]] = []

    def fake_run(command, **kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["cwd"] == root
        assert kwargs["env"]["KANSEI_DISABLE_VERSION_CHECK"] == "1"
        calls.append(tuple(command))
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr("kansei.update.chain.subprocess.run", fake_run)

    results = run_upgrade_chain(chain)

    assert len(results) == 2
    assert calls == [
        upgrade_step_command(root, "0.2.1"),
        upgrade_step_command(root, "0.3.0"),
    ]


def test_update_harness_plan_prints_upgrade_chain(tmp_path: Path, monkeypatch) -> None:
    root = init_instance(tmp_path / "kansei")

    def fake_build_chain(instance_root: Path, *, target: str):
        return build_upgrade_chain(
            instance_root,
            target=target,
            current_version="0.3.0",
            applied_version="0.1.0",
            fetch_versions=lambda: ("0.2.1", "0.3.0"),
        )

    monkeypatch.setattr(
        update_command,
        "build_upgrade_chain",
        fake_build_chain,
    )

    result = CliRunner().invoke(
        app,
        ["update-harness", "--root", str(root), "--plan", "--no-harnessops"],
    )

    assert result.exit_code == 0, result.stdout
    assert "planned upgrade chain:" in result.stdout
    assert "1. 0.1.0 -> 0.2.1" in result.stdout
    assert "2. 0.2.1 -> 0.3.0" in result.stdout
