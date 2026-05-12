from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from kansei import __version__

DEFAULT_INSTALL_SPEC = f"kansei=={__version__}"


@dataclass(frozen=True)
class BootstrapResult:
    created: tuple[str, ...]
    skipped: tuple[str, ...]
    warnings: tuple[str, ...]
    activation_hint: str

    @property
    def ok(self) -> bool:
        return not self.warnings


class BootstrapError(RuntimeError):
    pass


def bootstrap_environment(
    root: Path,
    *,
    install_spec: str = DEFAULT_INSTALL_SPEC,
    required: bool = False,
) -> BootstrapResult:
    uv = _find_uv()
    venv_dir = root / ".venv"
    python_path = python_in_venv(venv_dir)
    created: list[str] = []
    skipped: list[str] = []
    warnings: list[str] = []

    if venv_dir.exists():
        skipped.append(".venv")
    else:
        venv_result = _run_command([uv, "venv", str(venv_dir)], cwd=root)
        if venv_result.returncode == 0:
            created.append(".venv")
        else:
            warning = _format_warning("uv venv failed", venv_result)
            if required:
                raise BootstrapError(warning)
            warnings.append(warning)
            return BootstrapResult(
                created=tuple(created),
                skipped=tuple(skipped),
                warnings=tuple(warnings),
                activation_hint=activation_hint(),
            )

    install_result = _run_command(
        [uv, "pip", "install", install_spec, "--python", str(python_path)],
        cwd=root,
    )
    if install_result.returncode == 0:
        created.append(f"uv pip install {install_spec}")
    else:
        warning = _format_warning("kansei install failed", install_result)
        if required:
            raise BootstrapError(warning)
        warnings.append(warning)

    return BootstrapResult(
        created=tuple(created),
        skipped=tuple(skipped),
        warnings=tuple(warnings),
        activation_hint=activation_hint(),
    )


def python_in_venv(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def activation_hint() -> str:
    if sys.platform == "win32":
        return r".venv\Scripts\activate"
    return "source .venv/bin/activate"


def _find_uv() -> str:
    return shutil.which("uv") or "uv"


def _run_command(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _format_warning(label: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = (result.stderr or result.stdout or "").strip()
    if len(detail) > 300:
        detail = f"{detail[:300]}..."
    return f"{label}: {detail or f'exit code {result.returncode}'}"
