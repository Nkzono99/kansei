from __future__ import annotations

from typer.testing import CliRunner

from kansei.cli.commands.doctor import run_doctor
from kansei.cli.main import app
from kansei.core.instance import init_instance


def test_doctor_passes_after_init(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei", with_codex=True, with_mcp=True)

    report = run_doctor(root)

    assert report.ok
    assert report.errors == ()


def test_doctor_command_fails_when_required_file_missing(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")
    (root / "providers.toml").unlink()

    result = CliRunner().invoke(app, ["doctor", "--root", str(root)])

    assert result.exit_code == 1
    assert "missing file: providers.toml" in result.stderr


def test_doctor_warns_for_modified_managed_file(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")
    (root / "AGENTS.md").write_text("local edit\n", encoding="utf-8")

    report = run_doctor(root)

    assert report.ok
    assert "managed file has local edits: AGENTS.md" in report.warnings


def test_doctor_json_options(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")

    result = CliRunner().invoke(app, ["doctor", "--root", str(root), "--json", "--check-mcp"])

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert '"mcp": true' in result.stdout
