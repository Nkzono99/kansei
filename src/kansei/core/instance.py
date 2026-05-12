from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomli_w
from jinja2 import Environment, PackageLoader, select_autoescape

from kansei import __version__
from kansei.core.git import init_repo
from kansei.core.lockfile import ManagedFile, sha256_bytes, write_lock
from kansei.core.manifest import MANIFEST_PATH, default_manifest, write_manifest
from kansei.core.time import DEFAULT_TIMEZONE, today

ROOT_MARKERS = ("kansei.toml", str(MANIFEST_PATH))
TEMPLATE_VERSION = "0.1.0"


@dataclass(frozen=True)
class TemplateFile:
    path: str
    template: str
    file_class: str = "managed"


MANAGED_TEMPLATES: tuple[TemplateFile, ...] = (
    TemplateFile("AGENTS.md", "root/AGENTS.md.j2"),
    TemplateFile("KANSEI.md", "root/KANSEI.md.j2"),
    TemplateFile(".gitignore", "root/gitignore.j2", "generated"),
    TemplateFile(
        ".agents/skills/kansei-control-plane/SKILL.md",
        "agents/skills/kansei-control-plane/SKILL.md.j2",
    ),
    TemplateFile(
        ".agents/skills/kansei-control-plane/agents/openai.yaml",
        "agents/skills/kansei-control-plane/agents/openai.yaml.j2",
    ),
    TemplateFile(
        ".agents/skills/kansei-control-plane/references/control-plane-workflow.md",
        "agents/skills/kansei-control-plane/references/control-plane-workflow.md.j2",
    ),
    TemplateFile(
        ".agents/skills/kansei-control-plane/scripts/check_instance.py",
        "agents/skills/kansei-control-plane/scripts/check_instance.py.j2",
    ),
    TemplateFile(
        ".agents/skills/feedback-kansei/SKILL.md",
        "agents/skills/feedback-kansei/SKILL.md.j2",
    ),
    TemplateFile(
        ".agents/skills/feedback-kansei/agents/openai.yaml",
        "agents/skills/feedback-kansei/agents/openai.yaml.j2",
    ),
    TemplateFile("runbooks/_templates/project-runbook.md", "runbooks/project-runbook.md.j2"),
    TemplateFile("prompts/_templates/delegation.md", "prompts/delegation.md.j2"),
)


def codex_template() -> TemplateFile:
    return TemplateFile(".codex/config.toml", "root/codex-config.toml.j2", "generated")


def template_environment() -> Environment:
    return Environment(
        loader=PackageLoader("kansei", "templates"),
        autoescape=select_autoescape(default=False),
        keep_trailing_newline=True,
    )


def render_template(template: str, context: dict[str, Any]) -> str:
    return template_environment().get_template(template).render(**context)


def find_instance_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in (current, *current.parents):
        if all((path / marker).exists() for marker in ROOT_MARKERS):
            return path
    raise RuntimeError("not inside a Kansei instance")


def is_instance_root(path: Path) -> bool:
    return all((path / marker).exists() for marker in ROOT_MARKERS)


def init_instance(
    target: Path,
    *,
    use_git: bool = False,
    with_codex: bool = False,
    with_mcp: bool = False,
    force: bool = False,
) -> Path:
    root = target.expanduser().resolve()
    if root.exists() and any(root.iterdir()) and not force and not is_instance_root(root):
        raise FileExistsError(f"target is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)

    context = {
        "name": root.name,
        "root": root.as_posix(),
        "version": __version__,
        "template_version": TEMPLATE_VERSION,
        "timezone": DEFAULT_TIMEZONE,
        "today": today(),
        "with_mcp": with_mcp,
    }

    _write_user_file(root, "README.md", "root/README.md.j2", context)
    _write_user_file(root, "kansei.toml", "root/kansei.toml.j2", context)
    _write_user_file(root, "projects.toml", "root/projects.toml.j2", context)
    _write_user_file(root, "providers.toml", "root/providers.toml.j2", context)

    for directory in (
        "knowledge/project-notes",
        "knowledge/reading-notes",
        "dashboards",
        "runbooks",
        "prompts",
        ".kansei/state",
        ".kansei/cache",
        ".kansei/logs",
        ".kansei/backups",
        ".kansei/migrations",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)

    for path, template in {
        "knowledge/README.md": "knowledge/README.md.j2",
        "knowledge/profile.md": "knowledge/profile.md.j2",
        "knowledge/research-profile.md": "knowledge/research-profile.md.j2",
        "knowledge/writing-style.md": "knowledge/writing-style.md.j2",
        "knowledge/hpc.md": "knowledge/hpc.md.j2",
        "knowledge/collaborators.md": "knowledge/collaborators.md.j2",
        "knowledge/decision-log.md": "knowledge/decision-log.md.j2",
        "dashboards/today.md": "dashboards/today.md.j2",
        "dashboards/weekly.md": "dashboards/weekly.md.j2",
        "dashboards/project-status.md": "dashboards/project-status.md.j2",
        "dashboards/provider-status.md": "dashboards/provider-status.md.j2",
        "runbooks/daily-planning.md": "runbooks/daily-planning.md.j2",
        "runbooks/hpc-experiment.md": "runbooks/hpc-experiment.md.j2",
        "runbooks/paper-writing.md": "runbooks/paper-writing.md.j2",
        "runbooks/code-development.md": "runbooks/code-development.md.j2",
        "runbooks/feedback-routing.md": "runbooks/feedback-routing.md.j2",
        "prompts/daily-planning.md": "prompts/daily-planning.md.j2",
        "prompts/project-triage.md": "prompts/project-triage.md.j2",
        "prompts/paper-review.md": "prompts/paper-review.md.j2",
        "prompts/hpc-failure-triage.md": "prompts/hpc-failure-triage.md.j2",
        "prompts/codex-delegation.md": "prompts/codex-delegation.md.j2",
    }.items():
        _write_user_file(root, path, template, context)

    managed_templates = list(MANAGED_TEMPLATES)
    if with_codex:
        managed_templates.append(codex_template())

    lock: dict[str, ManagedFile] = {}
    for item in managed_templates:
        rendered = render_template(item.template, context)
        destination = root / item.path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rendered.encode("utf-8"))
        lock[item.path] = ManagedFile(
            path=item.path,
            template=item.template,
            version=TEMPLATE_VERSION,
            checksum=sha256_bytes(rendered.encode("utf-8")),
            file_class=item.file_class,
        )

    write_manifest(root, default_manifest(root, template_version=TEMPLATE_VERSION))
    write_lock(root, lock)

    if use_git:
        init_repo(root)

    return root


def load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def dump_toml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(tomli_w.dumps(data), encoding="utf-8")


def _write_user_file(root: Path, path: str, template: str, context: dict[str, Any]) -> None:
    destination = root / path
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_template(template, context), encoding="utf-8")
