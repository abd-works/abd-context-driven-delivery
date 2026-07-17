from __future__ import annotations

from pathlib import Path
from typing import Any

from .asset import Asset
from .asset_collection import AssetCollection
from .asset_location import AssetLocation, AssetLocator
from .markdown_extractor import read_file, read_section
from .instruction_routing import _slug_variants


class Instruction:
    def __init__(self, text: str, module_dir: Path, *, domain_slug: str | None = None) -> None:
        self.text = text.strip()
        self.module_dir = Path(module_dir)
        self.domain_slug = domain_slug or self.module_dir.name
        self._host: Any | None = None
        self._label: str | None = None
        self._collection = False
        self._group: str | None = None
        self._filter_key: str | None = None

    @classmethod
    def ref(
        cls,
        host: Any,
        label: str,
        *,
        collection: bool = False,
        group: str | None = None,
        filter_key: str | None = None,
    ) -> Instruction:
        module_dir = Path(getattr(host, "module_dir", Path(".")))
        domain_slug = getattr(host, "domain_slug", getattr(host, "toolset_name", module_dir.name))
        instruction = cls("", module_dir, domain_slug=domain_slug)
        instruction._host = host
        instruction._label = label
        instruction._collection = collection
        instruction._group = group
        instruction._filter_key = filter_key
        return instruction

    def expand(self) -> str:
        if self._label is not None and self._host is not None:
            return self._expand_ref()
        if not self.matches_file_or_folder():
            return self.text
        path_part, section = self._split_section()
        if path_part.startswith("§"):
            section = path_part.removeprefix("§").strip()
            path = self._canonical_markdown()
            return read_section(path, section) if section else read_file(path)
        resolved = self._resolve_path(path_part)
        if resolved.is_dir():
            location = AssetLocation(
                "folder", self.module_dir, self.domain_slug, folder=resolved.resolve()
            )
            return AssetCollection(location).merged()
        if resolved.is_file():
            return read_section(resolved, section) if section else read_file(resolved)
        candidate = Path(f"{resolved}.md")
        if candidate.is_file():
            return read_section(candidate, section) if section else read_file(candidate)
        return self.text

    def matches_file_or_folder(self) -> bool:
        if self._label is not None:
            return True
        if self.text.startswith("§"):
            return True
        path_part, _ = self._split_section()
        if not path_part or "\n" in path_part:
            return False
        resolved = self._resolve_path(path_part)
        if resolved.exists():
            return True
        return Path(f"{resolved}.md").is_file()

    def _expand_ref(self) -> str:
        location = AssetLocator(
            self._host,
            self._label or "",
            group=self._group,
            filter_key=self._filter_key,
        ).locate()
        # Folders always merge as a collection (includes .py scaffolds, not only .md).
        if self._collection or location.kind == "folder":
            return AssetCollection(location).merged()
        return Asset(location).collect()

    def _split_section(self) -> tuple[str, str]:
        if " § " in self.text:
            path_part, section = self.text.split(" § ", 1)
            return path_part.strip(), section.strip()
        return self.text, ""

    def _canonical_markdown(self) -> Path:
        for slug in _slug_variants(self.domain_slug):
            candidate = self.module_dir / f"{slug}.md"
            if candidate.is_file():
                return candidate
        return self.module_dir / f"{self.domain_slug}.md"

    def _resolve_path(self, path_part: str) -> Path:
        normalized = path_part.rstrip("/")
        return (self.module_dir / normalized).resolve()
