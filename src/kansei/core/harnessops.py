from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PROJECT_PROFILE = "generic-code"
PROJECT_FILE = Path(".harnessops") / "project.toml"


@dataclass(frozen=True)
class HarnessOpsResult:
    status: str
    args: tuple[str, ...]
    stdout: str = ""
    stderr: str = ""
    reason: str = ""

    @property
    def ran(self) -> bool:
        return self.status == "ran"


class HarnessOpsError(RuntimeError):
    pass


class HarnessOpsUnavailable(HarnessOpsError):
    pass


class HarnessOpsCommandError(HarnessOpsError):
    def __init__(self, args: tuple[str, ...], returncode: int, stdout: str, stderr: str) -> None:
        self.args_tuple = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        detail = stderr.strip() or stdout.strip() or f"exit code {returncode}"
        super().__init__(f"HarnessOps command failed ({' '.join(args)}): {detail}")


def run_harnessops_init(
    root: Path,
    *,
    profile: str = DEFAULT_PROJECT_PROFILE,
    with_agent_bridge: bool = False,
    required: bool = False,
) -> list[HarnessOpsResult]:
    if (root / PROJECT_FILE).exists():
        return [
            _run_hops(root, ("doctor", "--check-overlay", "--check-records"), required=required)
        ]

    args = ["init", "--profile", profile]
    if with_agent_bridge:
        args.append("--with-agent-bridge")
    return [_run_hops(root, tuple(args), required=required)]


def run_harnessops_update(
    root: Path,
    *,
    apply: bool = False,
    profile: str = DEFAULT_PROJECT_PROFILE,
    with_agent_bridge: bool = False,
    required: bool = False,
) -> list[HarnessOpsResult]:
    results: list[HarnessOpsResult] = []
    is_initialized = (root / PROJECT_FILE).exists()

    if not is_initialized:
        init_args = ["init", "--profile", profile]
        if with_agent_bridge:
            init_args.append("--with-agent-bridge")
        if not apply:
            init_args.append("--dry-run")
        results.append(_run_hops(root, tuple(init_args), required=required))

        if not apply or not results[-1].ran:
            return results

    update_args = ["update-harness"]
    if not apply:
        update_args.append("--dry-run")
    if with_agent_bridge:
        update_args.extend(("--agent-bridge", "--codex"))
    results.append(_run_hops(root, tuple(update_args), required=required))
    return results


def hops_is_available() -> bool:
    return _resolve_hops_command() is not None


def _run_hops(root: Path, args: tuple[str, ...], *, required: bool) -> HarnessOpsResult:
    command = _resolve_hops_command()
    if command is None:
        reason = (
            "hops command not found; install HarnessOps, set KANSEI_HOPS_COMMAND, "
            "or set KANSEI_HARNESSOPS_SOURCE"
        )
        if required:
            raise HarnessOpsUnavailable(reason)
        return HarnessOpsResult(status="skipped", args=args, reason=reason)

    process = subprocess.run(
        [*command, *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise HarnessOpsCommandError(args, process.returncode, process.stdout, process.stderr)
    return HarnessOpsResult(
        status="ran",
        args=args,
        stdout=process.stdout,
        stderr=process.stderr,
    )


def _resolve_hops_command(env: Mapping[str, str] | None = None) -> tuple[str, ...] | None:
    current_env = env or os.environ

    configured_command = current_env.get("KANSEI_HOPS_COMMAND")
    if configured_command:
        return tuple(shlex.split(configured_command, posix=os.name != "nt"))

    hops = shutil.which("hops")
    if hops:
        return (hops,)

    harnessops_source = current_env.get("KANSEI_HARNESSOPS_SOURCE")
    if harnessops_source:
        uvx = shutil.which("uvx")
        if uvx:
            return (uvx, "--isolated", "--from", harnessops_source, "hops")

    return None
