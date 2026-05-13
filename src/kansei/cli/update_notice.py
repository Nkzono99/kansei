"""Best-effort update notices for the ``kansei`` CLI."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from kansei import __version__
from kansei.core.instance import find_instance_root
from kansei.core.manifest import (
    PACKAGE_NAME,
    applied_harness_kansei_version,
    kansei_uvx_command,
)

_PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
_DISABLE_ENV = "KANSEI_DISABLE_VERSION_CHECK"
_FORCE_ENV = "KANSEI_FORCE_VERSION_CHECK"
_CACHE_ENV = "KANSEI_UPDATE_CHECK_CACHE"
_CHECK_INTERVAL = timedelta(hours=24)
_NOTICE_INTERVAL = timedelta(hours=24)


def maybe_emit_update_notice(
    *,
    command: str,
    argv: Sequence[str] | None = None,
    root: Path | None = None,
    json_output: bool = False,
) -> None:
    if json_output:
        return
    effective_argv = list(argv) if argv is not None else [command]
    if not should_check_for_update(
        effective_argv,
        env=os.environ,
        stderr_is_tty=sys.stderr.isatty(),
    ):
        return

    instance_root = root or _find_current_instance_root()
    message = build_update_notice(
        __version__,
        cache_path=default_cache_path(os.environ),
        instance_root=instance_root,
    )
    if message:
        sys.stderr.write(f"{message}\n")


def should_check_for_update(
    argv: Sequence[str],
    *,
    env: Mapping[str, str],
    stderr_is_tty: bool,
) -> bool:
    if env.get(_DISABLE_ENV):
        return False
    if env.get("CI"):
        return False
    if not stderr_is_tty and not env.get(_FORCE_ENV):
        return False
    if not argv:
        return False
    if any(item in {"--help", "-h", "--version", "--json"} for item in argv):
        return False

    command = argv[0]
    return command not in {"version", "update-harness", "mcp"}


def build_update_notice(
    current_version: str,
    *,
    cache_path: Path,
    instance_root: Path | None = None,
    applied_version: str | None = None,
    now: datetime | None = None,
    fetch_latest: Callable[[], str | None] | None = None,
) -> str | None:
    now = now or datetime.now(UTC)
    fetch_latest = fetch_latest or fetch_latest_version
    cache = _read_cache(cache_path)
    if applied_version is None and instance_root is not None:
        applied_version = applied_harness_kansei_version(instance_root)

    latest = _latest_from_fresh_cache(cache, now)
    if latest is None:
        latest = fetch_latest()
        cache["checked_at"] = _format_dt(now)
        if latest is not None:
            cache["latest_version"] = latest
        else:
            cache.pop("latest_version", None)
        _write_cache(cache_path, cache)

    notices = _build_notice_sections(
        current_version=current_version,
        latest_version=latest,
        applied_version=applied_version,
        instance_root=instance_root,
    )
    if not notices:
        return None

    notice_key = "|".join(notices)
    if not _should_emit_notice(cache, notice_key, now):
        return None

    cache["notice_version"] = notice_key
    cache["last_notice_at"] = _format_dt(now)
    _write_cache(cache_path, cache)
    return "\n".join(notices)


def fetch_latest_version(timeout: float = 1.0) -> str | None:
    request = urllib.request.Request(
        _PYPI_JSON_URL,
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
        return None

    if not isinstance(payload, dict):
        return None
    info = payload.get("info")
    if not isinstance(info, dict):
        return None
    version = info.get("version")
    return version if isinstance(version, str) and version else None


def default_cache_path(env: Mapping[str, str] | None = None) -> Path:
    env = env or os.environ
    override = env.get(_CACHE_ENV)
    if override:
        return Path(override).expanduser()

    cache_root = env.get("XDG_CACHE_HOME") or env.get("LOCALAPPDATA")
    if cache_root:
        return Path(cache_root) / "kansei" / "update-check.json"
    return Path.home() / ".cache" / "kansei" / "update-check.json"


def _build_notice_sections(
    *,
    current_version: str,
    latest_version: str | None,
    applied_version: str | None,
    instance_root: Path | None,
) -> list[str]:
    notices: list[str] = []
    latest_is_newer = latest_version is not None and _is_newer_version(
        latest_version,
        current_version,
    )
    update_target = (
        latest_version if latest_is_newer and latest_version is not None else current_version
    )

    if latest_is_newer and latest_version is not None:
        notices.extend(
            [
                f"A new Kansei release is available: {current_version} -> {latest_version}",
                "Preferred CLI flow:",
                f"  {kansei_uvx_command('<command>')}",
            ]
        )

    if applied_version is not None and _is_newer_version(update_target, applied_version):
        if notices:
            notices.append("")
        notices.extend(
            [
                "This instance's Kansei harness is older than the recommended "
                f"CLI version: {applied_version} -> {update_target}",
                "Preview managed harness changes with:",
                f"  {_update_harness_command(instance_root)}",
                "Use the instance skill `$kansei-control-plane` to review the "
                "preview and apply `update-harness --apply` when appropriate.",
            ]
        )
    elif applied_version is not None and _is_newer_version(applied_version, current_version):
        if notices:
            notices.append("")
        notices.extend(
            [
                "This instance harness was last applied with a newer Kansei "
                f"version ({applied_version}) than the CLI running now ({current_version}).",
                "You may be using an old project .venv `kansei`; prefer:",
                f"  {kansei_uvx_command('<command>')}",
            ]
        )

    if notices:
        notices.append(f"Set {_DISABLE_ENV}=1 to hide this notice.")
    return notices


def _update_harness_command(instance_root: Path | None) -> str:
    args = ["update-harness", "--plan"]
    if instance_root is not None:
        args.extend(("--root", str(instance_root)))
    return kansei_uvx_command(*args, refresh_package=True)


def _find_current_instance_root() -> Path | None:
    try:
        return find_instance_root()
    except RuntimeError:
        return None


def _latest_from_fresh_cache(cache: dict[str, Any], now: datetime) -> str | None:
    latest = cache.get("latest_version")
    checked_at = _parse_dt(cache.get("checked_at"))
    if not isinstance(latest, str) or checked_at is None:
        return None
    if now - checked_at > _CHECK_INTERVAL:
        return None
    return latest


def _should_emit_notice(cache: dict[str, Any], notice_key: str, now: datetime) -> bool:
    if cache.get("notice_version") != notice_key:
        return True
    last_notice_at = _parse_dt(cache.get("last_notice_at"))
    if last_notice_at is None:
        return True
    return now - last_notice_at >= _NOTICE_INTERVAL


def _read_cache(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_cache(path: Path, data: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return


def _parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _format_dt(value: datetime) -> str:
    return value.astimezone(UTC).isoformat()


def _is_newer_version(candidate: str, current: str) -> bool:
    candidate_release, candidate_stage, candidate_raw = _version_key(candidate)
    current_release, current_stage, current_raw = _version_key(current)
    width = max(len(candidate_release), len(current_release))
    padded_candidate = candidate_release + (0,) * (width - len(candidate_release))
    padded_current = current_release + (0,) * (width - len(current_release))
    return (padded_candidate, candidate_stage, candidate_raw) > (
        padded_current,
        current_stage,
        current_raw,
    )


def _version_key(version: str) -> tuple[tuple[int, ...], int, str]:
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
