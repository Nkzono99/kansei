from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

import tomli_w

LOCK_PATH = Path(".kansei") / "lock.toml"


@dataclass(frozen=True)
class ManagedFile:
    path: str
    template: str
    version: str
    checksum: str
    owner: str = "kansei"
    file_class: str = "managed"

    def to_toml(self) -> dict[str, str]:
        return {
            "path": self.path,
            "template": self.template,
            "version": self.version,
            "checksum": self.checksum,
            "owner": self.owner,
            "class": self.file_class,
        }


def sha256_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def load_lock(root: Path) -> dict[str, ManagedFile]:
    path = root / LOCK_PATH
    if not path.exists():
        return {}
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    files: dict[str, ManagedFile] = {}
    for item in data.get("managed_files", []):
        files[item["path"]] = ManagedFile(
            path=item["path"],
            template=item["template"],
            version=item["version"],
            checksum=item["checksum"],
            owner=item.get("owner", "kansei"),
            file_class=item.get("class", "managed"),
        )
    return files


def write_lock(root: Path, files: dict[str, ManagedFile]) -> None:
    lock_path = root / LOCK_PATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": "0.1",
        "managed_files": [file.to_toml() for file in sorted(files.values(), key=lambda f: f.path)],
    }
    lock_path.write_text(tomli_w.dumps(data), encoding="utf-8")

