from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from kansei.core.paths import find_instance_root, relative_to_root

DEFAULT_SEARCH_PATHS = ("knowledge", "runbooks", "prompts", "dashboards", "KANSEI.md")
TEXT_SUFFIXES = {".md", ".txt", ".toml", ".yaml", ".yml"}


class SearchHit(BaseModel):
    path: str
    line: int
    preview: str


class SearchResults(BaseModel):
    query: str
    hits: list[SearchHit]


def search_knowledge(
    query: str,
    root: Path | str | None = None,
    *,
    limit: int = 20,
    paths: tuple[str, ...] = DEFAULT_SEARCH_PATHS,
) -> SearchResults:
    instance_root = find_instance_root(Path(root) if root is not None else None)
    needle = query.casefold()
    if not needle:
        return SearchResults(query=query, hits=[])

    hits: list[SearchHit] = []
    for file_path in _iter_search_files(instance_root, paths):
        try:
            lines = file_path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if needle in line.casefold():
                hits.append(
                    SearchHit(
                        path=relative_to_root(instance_root, file_path),
                        line=line_number,
                        preview=line.strip(),
                    )
                )
                if len(hits) >= limit:
                    return SearchResults(query=query, hits=hits)
    return SearchResults(query=query, hits=hits)


def _iter_search_files(root: Path, paths: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = root / raw_path
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
        elif path.is_dir():
            files.extend(
                sorted(
                    child
                    for child in path.rglob("*")
                    if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES
                )
            )
    return files
