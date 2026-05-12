from __future__ import annotations

from dataclasses import dataclass

from kansei.core.bootstrap import bootstrap_environment, python_in_venv


@dataclass
class _CompletedProcess:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""


def test_bootstrap_creates_venv_and_installs_kansei(tmp_path, monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append(list(args))
        return _CompletedProcess()

    monkeypatch.setattr("kansei.core.bootstrap._find_uv", lambda: "/usr/bin/uv")
    monkeypatch.setattr("kansei.core.bootstrap.subprocess.run", fake_run)

    result = bootstrap_environment(tmp_path, install_spec="kansei==1.2.3")

    expected_python = str(python_in_venv(tmp_path / ".venv"))
    assert result.created == (".venv", "uv pip install kansei==1.2.3")
    assert result.skipped == ()
    assert result.warnings == ()
    assert calls == [
        ["/usr/bin/uv", "venv", str(tmp_path / ".venv")],
        ["/usr/bin/uv", "pip", "install", "kansei==1.2.3", "--python", expected_python],
    ]


def test_bootstrap_skips_existing_venv(tmp_path, monkeypatch) -> None:
    (tmp_path / ".venv").mkdir()
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append(list(args))
        return _CompletedProcess()

    monkeypatch.setattr("kansei.core.bootstrap._find_uv", lambda: "uv")
    monkeypatch.setattr("kansei.core.bootstrap.subprocess.run", fake_run)

    result = bootstrap_environment(tmp_path, install_spec="kansei")

    assert result.created == ("uv pip install kansei",)
    assert result.skipped == (".venv",)
    assert calls == [
        ["uv", "pip", "install", "kansei", "--python", str(python_in_venv(tmp_path / ".venv"))]
    ]


def test_bootstrap_warns_when_venv_creation_fails(tmp_path, monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):  # type: ignore[no-untyped-def]
        calls.append(list(args))
        return _CompletedProcess(returncode=1, stderr="venv failed")

    monkeypatch.setattr("kansei.core.bootstrap._find_uv", lambda: "uv")
    monkeypatch.setattr("kansei.core.bootstrap.subprocess.run", fake_run)

    result = bootstrap_environment(tmp_path, install_spec="kansei")

    assert result.created == ()
    assert result.warnings == ("uv venv failed: venv failed",)
    assert calls == [["uv", "venv", str(tmp_path / ".venv")]]
