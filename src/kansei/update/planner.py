from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kansei.core.instance import TEMPLATE_VERSION, render_template
from kansei.core.lockfile import ManagedFile, load_lock, sha256_bytes, sha256_file
from kansei.core.time import DEFAULT_TIMEZONE, today
from kansei.update.managed_files import managed_templates


@dataclass(frozen=True)
class UpdateAction:
    path: str
    template: str
    action: str
    reason: str
    content: str
    new_path: str | None = None


@dataclass(frozen=True)
class UpdatePlan:
    root: Path
    actions: tuple[UpdateAction, ...]

    @property
    def has_changes(self) -> bool:
        return any(action.action != "unchanged" for action in self.actions)


def plan_update(root: Path) -> UpdatePlan:
    lock = load_lock(root)
    context = {
        "name": root.name,
        "root": root.as_posix(),
        "version": TEMPLATE_VERSION,
        "template_version": TEMPLATE_VERSION,
        "timezone": DEFAULT_TIMEZONE,
        "today": today(),
        "with_mcp": True,
    }

    actions: list[UpdateAction] = []
    for item in managed_templates(include_codex=(root / ".codex" / "config.toml").exists()):
        desired = render_template(item.template, context)
        desired_checksum = sha256_bytes(desired.encode("utf-8"))
        destination = root / item.path
        locked = lock.get(item.path)

        if not destination.exists():
            actions.append(
                UpdateAction(item.path, item.template, "create", "managed file is missing", desired)
            )
            continue

        current_checksum = sha256_file(destination)
        if current_checksum == desired_checksum:
            actions.append(
                UpdateAction(item.path, item.template, "unchanged", "already current", desired)
            )
            continue

        if locked is not None and current_checksum == locked.checksum:
            actions.append(
                UpdateAction(
                    item.path,
                    item.template,
                    "update",
                    "managed file matches lock and template changed",
                    desired,
                )
            )
            continue

        actions.append(
            UpdateAction(
                item.path,
                item.template,
                "write_new",
                "existing managed file has local edits",
                desired,
                new_path=f"{item.path}.new",
            )
        )

    return UpdatePlan(root=root, actions=tuple(actions))


def managed_file_for(action: UpdateAction) -> ManagedFile:
    return ManagedFile(
        path=action.path,
        template=action.template,
        version=TEMPLATE_VERSION,
        checksum=sha256_bytes(action.content.encode("utf-8")),
    )
