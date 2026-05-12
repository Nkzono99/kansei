from __future__ import annotations

from kansei.providers.base import ProviderAdapter
from kansei.providers.generic_code import GenericCodeProvider


def get_builtin_provider(provider_id: str) -> ProviderAdapter:
    normalized = provider_id.replace("_", "-")
    if normalized in {"generic-code", "kansei", "harnessops", "paperops", "runops"}:
        return GenericCodeProvider(provider_id=provider_id)
    return GenericCodeProvider(provider_id="generic-code")
