from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .instruction_routing import active_resource, path_for_template

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
        domain_slug = getattr(self.host, "toolset_name", getattr(self.host, "domain_slug", module_dir.name))
        filter_value = active_resource(self.host, self.filter_key) if self.filter_key else None
        if self.label == "template":
            return _locate_template(module_dir, domain_slug, filter_value)
        search_root = _search_root(module_dir, self.group, filter_value)
        return _locate_under(search_root, module_dir, domain_slug, self.label)


def _search_root(module_dir: Path, group: str | None, filter_value: str | None) -> Path:
    root = module_dir
    if group:
        root = root / group
    if filter_value:
        root = root / filter_value
    return root


def _locate_under(search_root: Path, module_dir: Path, domain_slug: str, label: str) -> AssetLocation:
    if label == "domain_generate":
        section_file = module_dir / f"{domain_slug}.md"
        if not section_file.is_file():
            section_file = search_root / f"{domain_slug}.md"
        return AssetLocation(
            "section",
            module_dir,
            domain_slug,
            section_file=section_file.resolve(),
            section_heading="Generate",
        )
    folder = search_root / label
    if folder.is_dir():
        return AssetLocation("folder", module_dir, domain_slug, folder=folder.resolve())
    if label == "rules":
        return AssetLocation("folder", module_dir, domain_slug, folder=folder.resolve())
    if label == "templates":
        return AssetLocation("folder", module_dir, domain_slug, folder=folder.resolve())
    for name in (label, f"{label}.md"):
        candidate = search_root / name
        if candidate.is_file():
            return AssetLocation("file", module_dir, domain_slug, path=candidate.resolve())
    section_file = search_root / f"{domain_slug}.md"
    if not section_file.is_file():
        section_file = module_dir / f"{domain_slug}.md"
    return AssetLocation(
        "section",
        module_dir,
        domain_slug,
        section_file=section_file.resolve(),
        section_heading=label.title(),
    )


def _locate_template(module_dir: Path, domain_slug: str, active_format: str | None) -> AssetLocation:
    if active_format:
        format_dir = module_dir / "formats" / active_format
        if format_dir.is_dir():
            template_stem = f"{domain_slug}-template"
            for path in sorted(format_dir.glob(f"{template_stem}.*")):
                return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
    relative = path_for_template(module_dir, domain_slug, active_format)
    resolved = (module_dir / relative).resolve()
    if resolved.is_file():
        return AssetLocation("file", module_dir, domain_slug, path=resolved)
    return AssetLocation("file", module_dir, domain_slug, path=resolved)
