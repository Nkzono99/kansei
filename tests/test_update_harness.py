from __future__ import annotations

import tomllib

from typer.testing import CliRunner

from kansei.cli.main import app
from kansei.core.instance import init_instance
from kansei.update.applier import apply_update
from kansei.update.planner import plan_update


def test_update_harness_dry_run_noop_on_fresh_instance(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei", with_codex=True)

    result = CliRunner().invoke(app, ["update-harness", "--root", str(root)])

    assert result.exit_code == 0
    assert "up to date" in result.stdout


def test_update_harness_creates_missing_managed_file(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")
    (root / ".agents" / "skills" / "feedback-kansei" / "SKILL.md").unlink()

    plan = plan_update(root)
    assert any(
        action.path == ".agents/skills/feedback-kansei/SKILL.md" and action.action == "create"
        for action in plan.actions
    )

    apply_update(plan)
    assert (root / ".agents" / "skills" / "feedback-kansei" / "SKILL.md").exists()


def test_update_harness_writes_new_for_user_modified_managed_file(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")
    original = (root / "AGENTS.md").read_text(encoding="utf-8")
    (root / "AGENTS.md").write_text(original + "\nLocal note.\n", encoding="utf-8")

    result = CliRunner().invoke(app, ["update-harness", "--root", str(root), "--apply"])

    assert result.exit_code == 0
    assert (root / "AGENTS.md.new").exists()
    assert (root / "AGENTS.md").read_text(encoding="utf-8").endswith("Local note.\n")


def test_update_harness_does_not_touch_user_owned_registry(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")
    projects = root / "projects.toml"
    projects.write_text(projects.read_text(encoding="utf-8") + "\n# user note\n", encoding="utf-8")

    result = CliRunner().invoke(app, ["update-harness", "--root", str(root), "--apply"])

    assert result.exit_code == 0
    assert "# user note" in projects.read_text(encoding="utf-8")
    assert not (root / "projects.toml.new").exists()


def test_update_harness_apply_refreshes_manifest_metadata(tmp_path) -> None:
    root = init_instance(tmp_path / "kansei")
    manifest_path = root / ".kansei" / "manifest.toml"
    manifest_path.write_text(
        manifest_path.read_text(encoding="utf-8")
        .replace('kansei_version = "0.1.0"', 'kansei_version = "0.0.1"')
        .replace('runner = "uvx"', 'runner = "venv"')
        .replace('command = "uvx --from kansei kansei"', 'command = "kansei"'),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        app,
        ["update-harness", "--root", str(root), "--apply", "--no-harnessops"],
    )

    assert result.exit_code == 0, result.stdout
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["harness"]["kansei_version"] == "0.1.0"
    assert manifest["cli"]["runner"] == "uvx"
    assert manifest["cli"]["command"] == "uvx --from kansei kansei"
