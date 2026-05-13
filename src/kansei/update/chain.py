from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kansei import __version__
from kansei.core.manifest import CONSOLE_SCRIPT, PACKAGE_NAME, applied_harness_kansei_version

PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"


@dataclass(frozen=True)
class UpgradeStep:
    from_version: str
    to_version: str

    @property
    def crosses_major(self) -> bool:
        return major_version(self.from_version) != major_version(self.to_version)


@dataclass(frozen=True)
class UpgradeChain:
    root: Path
    applied_version: str | None
    current_version: str
    target_version: str
    target_source: str
    available_versions: tuple[str, ...]
    steps: tuple[UpgradeStep, ...]

    @property
    def has_steps(self) -> bool:
        return bool(self.steps)

    @property
    def crosses_major(self) -> bool:
        return any(step.crosses_major for step in self.steps)


@dataclass(frozen=True)
class UpgradeStepResult:
    step: UpgradeStep
    command: tuple[str, ...]
    stdout: str
    stderr: str


class UpgradeChainError(RuntimeError):
    pass


def build_upgrade_chain(
    root: Path,
    *,
    target: str = "latest",
    current_version: str = __version__,
    fetch_versions: Callable[[], Sequence[str]] | None = None,
    applied_version: str | None = None,
) -> UpgradeChain:
    releases = tuple(sorted_versions(fetch_versions() if fetch_versions else fetch_pypi_versions()))
    source_version = applied_version
    if source_version is None:
        source_version = applied_harness_kansei_version(root)

    target_version, target_source = resolve_target_version(
        target,
        releases=releases,
        current_version=current_version,
    )
    if source_version is None:
        source_version = current_version

    checkpoints = checkpoint_versions(
        source_version,
        target_version,
        releases=(*releases, current_version, target_version),
    )
    steps = []
    previous = source_version
    for checkpoint in checkpoints:
        steps.append(UpgradeStep(previous, checkpoint))
        previous = checkpoint

    return UpgradeChain(
        root=root,
        applied_version=source_version,
        current_version=current_version,
        target_version=target_version,
        target_source=target_source,
        available_versions=releases,
        steps=tuple(steps),
    )


def run_upgrade_chain(
    chain: UpgradeChain,
    *,
    allow_major: bool = False,
) -> tuple[UpgradeStepResult, ...]:
    if chain.crosses_major and not allow_major:
        raise UpgradeChainError(
            "planned upgrade chain crosses a major version boundary; rerun with --allow-major"
        )

    results: list[UpgradeStepResult] = []
    for step in chain.steps:
        command = upgrade_step_command(chain.root, step.to_version)
        env = dict(os.environ)
        env["KANSEI_DISABLE_VERSION_CHECK"] = "1"
        process = subprocess.run(
            list(command),
            cwd=chain.root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            detail = (
                process.stderr.strip()
                or process.stdout.strip()
                or f"exit code {process.returncode}"
            )
            raise UpgradeChainError(
                f"upgrade step failed ({step.from_version} -> {step.to_version}): {detail}"
            )
        results.append(
            UpgradeStepResult(
                step=step,
                command=command,
                stdout=process.stdout,
                stderr=process.stderr,
            )
        )
    return tuple(results)


def upgrade_step_command(root: Path, version: str) -> tuple[str, ...]:
    return (
        "uvx",
        "--from",
        f"{PACKAGE_NAME}=={version}",
        CONSOLE_SCRIPT,
        "update-harness",
        "--root",
        str(root),
        "--upgrade-step",
        "--no-harnessops",
    )


def fetch_pypi_versions(timeout: float = 2.0) -> tuple[str, ...]:
    request = urllib.request.Request(
        PYPI_JSON_URL,
        headers={"Accept": "application/json", "User-Agent": f"kansei/{__version__}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (
        OSError,
        TimeoutError,
        urllib.error.URLError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        return ()

    if not isinstance(payload, dict):
        return ()
    releases = payload.get("releases")
    if not isinstance(releases, dict):
        return ()
    return tuple(sorted_versions(version for version in releases if is_final_release(version)))


def resolve_target_version(
    target: str,
    *,
    releases: Sequence[str],
    current_version: str,
) -> tuple[str, str]:
    normalized = target.strip()
    if not normalized or normalized == "latest":
        if releases:
            return max(releases, key=version_key), "pypi-latest"
        return current_version, "current-runtime"

    if is_minor_target(normalized):
        candidates = [
            version
            for version in (*releases, current_version)
            if minor_prefix(version) == normalized
        ]
        if not candidates:
            raise UpgradeChainError(f"no known Kansei release matches target minor: {normalized}")
        return max(candidates, key=version_key), f"minor {normalized}"

    return normalized.lstrip("v"), "explicit"


def checkpoint_versions(
    from_version: str,
    to_version: str,
    *,
    releases: Sequence[str],
) -> tuple[str, ...]:
    if not is_newer_version(to_version, from_version):
        return ()

    candidates = {
        version
        for version in releases
        if is_newer_version(version, from_version) and not is_newer_version(version, to_version)
    }
    candidates.add(to_version)

    by_minor: dict[tuple[int, int], str] = {}
    for version in candidates:
        minor = major_minor(version)
        existing = by_minor.get(minor)
        if existing is None or is_newer_version(version, existing):
            by_minor[minor] = version
    return tuple(sorted_versions(by_minor.values()))


def sorted_versions(versions: Sequence[str] | Any) -> tuple[str, ...]:
    unique = {str(version).strip().lstrip("v") for version in versions if str(version).strip()}
    return tuple(sorted(unique, key=version_key))


def is_newer_version(candidate: str, current: str) -> bool:
    return version_key(candidate) > version_key(current)


def major_version(version: str) -> int:
    release, _stage, _raw = version_key(version)
    return release[0] if release else 0


def major_minor(version: str) -> tuple[int, int]:
    release, _stage, _raw = version_key(version)
    major = release[0] if release else 0
    minor = release[1] if len(release) > 1 else 0
    return major, minor


def minor_prefix(version: str) -> str:
    major, minor = major_minor(version)
    return f"{major}.{minor}"


def is_minor_target(value: str) -> bool:
    return re.fullmatch(r"v?\d+\.\d+", value) is not None


def is_final_release(version: str) -> bool:
    normalized = version.strip().lower().lstrip("v")
    return re.search(r"(?:a|b|rc|dev)", normalized) is None


def version_key(version: str) -> tuple[tuple[int, ...], int, str]:
    normalized = version.strip().lower()
    if normalized.startswith("v"):
        normalized = normalized[1:]
    public = normalized.split("+", 1)[0]
    release = re.split(r"(?:a|b|rc|dev|-)", public, maxsplit=1)[0]
    parts: list[int] = []
    for raw in release.split("."):
        match = re.match(r"\d+", raw)
        if match is None:
            break
        parts.append(int(match.group(0)))
    stage = -1 if re.search(r"(?:a|b|rc|dev)", public) else 0
    return tuple(parts), stage, normalized
