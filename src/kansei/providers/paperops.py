from __future__ import annotations

from kansei.providers.cli_domain import DomainCliProvider


class PaperOpsProvider(DomainCliProvider):
    def __init__(self, provider_id: str = "paperops") -> None:
        super().__init__(provider_id=provider_id, command_name="pops", domain_name="paperops")
