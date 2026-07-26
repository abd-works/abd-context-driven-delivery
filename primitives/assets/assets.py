"""Asset location and collection for instruction expansion."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from primitives.instructions import (
    _FORMAT_TEMPLATE_EXT,
    _active_resource,
    _path_for_templates,
    _slug_variants,
)

LocationKind = Literal["file", "folder", "section"]


@dataclass(frozen=True)
class AssetLocation:
    kind: LocationKind
    module_dir: Path
    domain_slug: str
    path: Path | None = None
    folder: Path | None = None
    section_file: Path | None = None
    section_heading: str | None = None


class AssetLocator:
    def __init__(
        self,
        host: Any,
        label: str,
        *,
        group: str | None = None,
        filter_key: str | None = None,
    ) -> None:
        self.host = host
        self.label = label
        self.group = group
        self.filter_key = filter_key

    def locate(self) -> AssetLocation:
        module_dir = Path(getattr(self.host, "module_dir", Path(".")))
        domain_slug = getattr(self.host, "domain_slug", getattr(self.host, "toolset_name", module_dir.name))
        filter_value = _active_resource(self.host, self.filter_key) if self.filter_key else None
        if self.label == "templates":
            # Prefer host.format so py/js/md template files are selected by channel.
            active_format = filter_value or _active_resource(self.host, "format")
            located = _locate_templates(module_dir, domain_slug, active_format)
            if located.path is not None and located.path.is_file():
                return located
            # Meta scaffold pack (e.g. context_tools/base/templates/) when no format artifact exists.
            meta = module_dir / "templates"
            if meta.is_dir():
                return AssetLocation("folder", module_dir, domain_slug, folder=meta.resolve())
        # Same lookup with or without a filter: optional group → filter subfolder → label.
        search_root = _search_root(module_dir, self.group, filter_value)
        return _locate_under(search_root, module_dir, domain_slug, self.label)


def _search_root(module_dir: Path, group: str | None, filter_value: str | None) -> Path:
    """Resolve module_dir[/group][/filter_value].

    filter_value selects a subdirectory under the group (e.g. fidelities/language/).
    If that directory is missing but a single file stem matches, use the group folder
    and let label lookup find `{filter_value}.*` only when the label equals the stem —
    otherwise prefer the directory layout.
    """
    root = module_dir
    if group:
        root = root / group
    if not filter_value:
        return root
    as_dir = root / filter_value
    if as_dir.is_dir():
        return as_dir
    return root


def _locate_under(search_root: Path, module_dir: Path, domain_slug: str, label: str) -> AssetLocation:
    folder = search_root / label
    if folder.is_dir():
        return AssetLocation("folder", module_dir, domain_slug, folder=folder.resolve())
    for name in (label, f"{label}.md"):
        candidate = search_root / name
        if candidate.is_file():
            return AssetLocation("file", module_dir, domain_slug, path=candidate.resolve())
    # Any extension: context_tools.md, examples.py, examples.ts, …
    matches = sorted(
        p for p in search_root.glob(f"{label}.*") if p.is_file()
    ) if search_root.is_dir() else []
    if matches:
        return AssetLocation("file", module_dir, domain_slug, path=matches[0].resolve())
    section_file = _canonical_domain_md(module_dir, search_root, domain_slug)
    return AssetLocation(
        "section",
        module_dir,
        domain_slug,
        section_file=section_file.resolve(),
        section_heading=label.title(),
    )


def _canonical_domain_md(module_dir: Path, search_root: Path, domain_slug: str) -> Path:
    for root in (module_dir, search_root):
        for slug in _slug_variants(domain_slug):
            candidate = root / f"{slug}.md"
            if candidate.is_file():
                return candidate
    return module_dir / f"{domain_slug}.md"


def _locate_templates(module_dir: Path, domain_slug: str, active_format: str | None) -> AssetLocation:
    stems = [
        f"{slug}-{suffix}"
        for slug in _slug_variants(domain_slug)
        for suffix in ("templates", "template")
    ]
    shared = module_dir / "templates"
    if shared.is_dir():
        # Prefer the format-specific template file when present (py / js / md / …).
        ext = _FORMAT_TEMPLATE_EXT.get(active_format or "", "")
        if ext:
            for stem in stems:
                path = shared / f"{stem}{ext}"
                if path.is_file():
                    return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
        return AssetLocation("folder", module_dir, domain_slug, folder=shared.resolve())
    if active_format:
        format_dir = module_dir / "formats" / active_format
        if format_dir.is_dir():
            for stem in stems:
                for path in sorted(format_dir.glob(f"{stem}.*")):
                    return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
    for stem in stems:
        for path in sorted(module_dir.glob(f"{stem}.*")):
            return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
    relative = _path_for_templates(module_dir, domain_slug, active_format)
    resolved = (module_dir / relative).resolve()
    return AssetLocation("file", module_dir, domain_slug, path=resolved)


class Asset:
    def __init__(self, location: AssetLocation) -> None:
        self.location = location

    def collect(self) -> str:
        from .markdown_extractor import _extract_single

        return _extract_single(self.location)


class AssetCollection:
    def __init__(self, location: AssetLocation) -> None:
        self.location = location
        self.collection: dict[str, str] = {}

    def collect(self) -> dict[str, str]:
        from .markdown_extractor import _extract_collection

        self.collection = _extract_collection(self.location)
        return self.collection

    def merged(self) -> str:
        from .markdown_extractor import _merge_collection

        if not self.collection:
            self.collect()
        return _merge_collection(self.collection)
