from __future__ import annotations

from kansei.providers.base import ProviderAdapter
from kansei.providers.generic_code import GenericCodeProvider
from kansei.providers.harnessops import HarnessOpsProvider
from kansei.providers.paperops import PaperOpsProvider
from kansei.providers.runops import RunOpsProvider


def get_builtin_provider(provider_id: str) -> ProviderAdapter:
    normalized = provider_id.replace("_", "-")
    if normalized == "harnessops":
        return HarnessOpsProvider(provider_id=provider_id)
    if normalized == "paperops":
        return PaperOpsProvider(provider_id=provider_id)
    if normalized in {"runops", "runops-hpc"}:
        return RunOpsProvider(provider_id=provider_id)
    if normalized in {"generic-code", "kansei"}:
        return GenericCodeProvider(provider_id=provider_id)
    return GenericCodeProvider(provider_id="generic-code")
