from __future__ import annotations

from kansei.providers.cli_domain import DomainCliProvider


class HarnessOpsProvider(DomainCliProvider):
    def __init__(self, provider_id: str = "harnessops") -> None:
        super().__init__(provider_id=provider_id, command_name="hops", domain_name="HarnessOps")
