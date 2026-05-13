from __future__ import annotations

from datetime import UTC, datetime

from kansei.cli.update_notice import build_update_notice, should_check_for_update


def test_update_notice_points_to_control_plane_skill(tmp_path) -> None:
    message = build_update_notice(
        "0.1.0",
        cache_path=tmp_path / "cache.json",
        now=datetime(2026, 5, 13, tzinfo=UTC),
        fetch_latest=lambda: "0.1.1",
        applied_version="0.1.0",
    )

    assert message is not None
    assert "0.1.0 -> 0.1.1" in message
    assert "$kansei-control-plane" in message
    assert "uvx --from kansei kansei <command>" in message
    assert "uvx --refresh-package kansei --from kansei kansei update-harness --plan" in message


def test_update_notice_reports_stale_instance_harness(tmp_path) -> None:
    message = build_update_notice(
        "0.1.1",
        cache_path=tmp_path / "cache.json",
        now=datetime(2026, 5, 13, tzinfo=UTC),
        fetch_latest=lambda: None,
        applied_version="0.1.0",
    )

    assert message is not None
    assert "Kansei harness is older" in message
    assert "0.1.0 -> 0.1.1" in message
    assert "update-harness" in message


def test_update_notice_warns_about_older_cli_than_harness(tmp_path) -> None:
    message = build_update_notice(
        "0.1.0",
        cache_path=tmp_path / "cache.json",
        now=datetime(2026, 5, 13, tzinfo=UTC),
        fetch_latest=lambda: None,
        applied_version="0.1.1",
    )

    assert message is not None
    assert "newer Kansei version (0.1.1)" in message
    assert "uvx --from kansei kansei <command>" in message


def test_update_notice_is_throttled_by_cache(tmp_path) -> None:
    cache_path = tmp_path / "cache.json"
    now = datetime(2026, 5, 13, tzinfo=UTC)

    first = build_update_notice(
        "0.1.0",
        cache_path=cache_path,
        now=now,
        fetch_latest=lambda: "0.1.1",
    )
    repeated = build_update_notice(
        "0.1.0",
        cache_path=cache_path,
        now=now,
        fetch_latest=lambda: "0.1.1",
    )

    assert first is not None
    assert repeated is None


def test_update_notice_skips_machine_readable_invocations() -> None:
    assert not should_check_for_update(["doctor", "--json"], env={}, stderr_is_tty=True)
    assert not should_check_for_update(
        ["mcp", "serve", "--transport", "stdio"],
        env={},
        stderr_is_tty=True,
    )
