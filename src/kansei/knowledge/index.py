from __future__ import annotations

from pathlib import Path

from kansei.knowledge.search import SearchResults, search_knowledge


def query(query_text: str, root: Path | str | None = None, *, limit: int = 20) -> SearchResults:
    return search_knowledge(query_text, root, limit=limit)
