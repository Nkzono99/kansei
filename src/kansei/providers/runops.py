from __future__ import annotations

from kansei.providers.cli_domain import DomainCliProvider


class RunOpsProvider(DomainCliProvider):
    def __init__(self, provider_id: str = "runops") -> None:
        super().__init__(provider_id=provider_id, command_name="runo", domain_name="runops")
