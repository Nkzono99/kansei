from __future__ import annotations

import json

import typer

from kansei.knowledge.search import search_knowledge


def search(query: str, limit: int = 20) -> None:
    typer.echo(json.dumps(search_knowledge(query, limit=limit).model_dump(), indent=2))
