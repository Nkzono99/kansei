from __future__ import annotations

from typer.testing import CliRunner

from kansei.cli.main import app


def test_version() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.2.0" in result.stdout
