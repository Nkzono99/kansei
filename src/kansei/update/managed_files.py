from __future__ import annotations

from kansei.core.instance import MANAGED_TEMPLATES, TemplateFile, codex_template


def managed_templates(*, include_codex: bool = True) -> tuple[TemplateFile, ...]:
    items = list(MANAGED_TEMPLATES)
    if include_codex:
        items.append(codex_template())
    return tuple(items)

