"""Asset location and collection for instruction expansion.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from primitives.instructions import (
    _FORMAT_TEMPLATE_EXT,
    _active_resource,
    _path_for_templates,
    _slug_variants,
)

LocationKind = Literal["file", "folder", "section"]

_FORMAT_DIR_ALIAS = {
    "markdown": "md",
    "python": "py",
    "typescript": "ts",
    "javascript": "js",
    "java": "java",
}

# Filename stems kept when host.format is set and templates/{alias}/ is a folder pack.
_FIDELITY_TEMPLATE_STEMS: dict[str, frozenset[str]] = {
    "story_map": frozenset({"story-map", "thin-slice"}),
    "scenarios": frozenset(
        {"scenario-inline", "scenario-main-flow", "scenario-outline"}
    ),
}

# Frontmatter `artifact:` values that mark a file as belonging to a fidelity
# (e.g. story-context.md is story_map; components/story-header.md is scenarios).
_FIDELITY_TEMPLATE_ARTIFACTS: dict[str, frozenset[str]] = {
    "story_map": frozenset({"story-map", "thin-slice"}),
    "scenarios": frozenset({"story-scenarios"}),
}


@dataclass(frozen=True)
class AssetLocation:
    kind: LocationKind
    module_dir: Path
    domain_slug: str
    path: Path | None = None
    folder: Path | None = None
    section_file: Path | None = None
    section_heading: str | None = None
    label: str | None = None
    fidelity: str | None = None
    format: str | None = None


class AssetLocator:
    def __init__(
        self,
        host: Any,
        label: str,
        *,
        group: str | None = None,
        filter_key: str | None = None,
        collection: bool = False,
    ) -> None:
        self._host = host
        self._label = label
        self._group = group
        self._filter_key = filter_key
        self._collection = collection

    @property
    def fidelity(self) -> str | None:
        return _active_resource(self._host, "fidelity")

    @property
    def format(self) -> str | None:
        fmt = _active_resource(self._host, "format")
        if fmt:
            return fmt
        fidelity = self.fidelity
        defaults = getattr(type(self._host), "_fidelity_format_defaults", None) or {}
        if not defaults:
            defaults = getattr(self._host, "_fidelity_format_defaults", {}) or {}
        if fidelity and fidelity in defaults:
            return str(defaults[fidelity])
        return None

    @property
    def contexts(self) -> str:
        return self._for_label("contexts").expand()

    @property
    def examples(self) -> str:
        return self._for_label("examples").expand()

    @property
    def templates(self) -> str:
        return self._for_label("templates").expand()

    def _for_label(self, label: str) -> AssetLocator:
        return AssetLocator(
            self._host,
            label,
            group=self._group,
            filter_key=self._filter_key,
            collection=self._collection,
        )

    def expand(self) -> str:
        """Locate this slot and merge it, already filtered for fidelity/format."""
        location = self.locate()
        if self._collection or location.kind == "folder":
            return AssetCollection(location).merged()
        return Asset(location).collect()

    def _stamp(self, location: AssetLocation) -> AssetLocation:
        return replace(
            location,
            label=self._label,
            fidelity=location.fidelity or self.fidelity,
            format=location.format or self.format,
        )

    def locate(self) -> AssetLocation:
        return self._stamp(self._locate())

    def _locate(self) -> AssetLocation:
        module_dir = Path(getattr(self._host, "module_dir", Path(".")))
        domain_slug = getattr(self._host, "domain_slug", getattr(self._host, "toolset_name", module_dir.name))
        filter_value = _active_resource(self._host, self._filter_key) if self._filter_key else None
        if self._label == "templates":
            # Prefer host.format so py/js/md template files are selected by channel.
            active_format = filter_value or _active_resource(self._host, "format")
            located = self._locate_templates(module_dir, domain_slug, active_format)
            if located.path is not None and located.path.is_file():
                return located
            if located.folder is not None and located.folder.is_dir():
                return located
            # Meta scaffold pack (e.g. context_tools/base/templates/) when no format artifact exists.
            meta = module_dir / "templates"
            if meta.is_dir():
                return AssetLocation("folder", module_dir, domain_slug, folder=meta.resolve())
        # Same lookup with or without a filter: optional group -> filter subfolder -> label.
        search_root = self._search_root(module_dir, filter_value)
        return self._locate_under(search_root, module_dir, domain_slug)

    def _search_root(self, module_dir: Path, filter_value: str | None) -> Path:
        """Resolve module_dir[/group][/filter_value].

        filter_value selects a subdirectory under the group (e.g. fidelities/language/).
        If that directory is missing but a single file stem matches, use the group folder
        and let label lookup find `{filter_value}.*` only when the label equals the stem -
        otherwise prefer the directory layout.
        """
        root = module_dir
        if self._group:
            root = root / self._group
        if not filter_value:
            return root
        as_dir = root / filter_value
        if as_dir.is_dir():
            return as_dir
        return root

    def _locate_under(self, search_root: Path, module_dir: Path, domain_slug: str) -> AssetLocation:
        folder = search_root / self._label
        if folder.is_dir():
            return AssetLocation("folder", module_dir, domain_slug, folder=folder.resolve())
        for name in (self._label, f"{self._label}.md"):
            candidate = search_root / name
            if candidate.is_file():
                return AssetLocation("file", module_dir, domain_slug, path=candidate.resolve())
        first = self._first_extension_match(search_root)
        if first:
            return AssetLocation("file", module_dir, domain_slug, path=first.resolve())
        section_file = self._canonical_domain_md(module_dir, search_root, domain_slug)
        return AssetLocation(
            "section",
            module_dir,
            domain_slug,
            section_file=section_file.resolve(),
            section_heading=self._label.replace("_", " ").replace("-", " ").title(),
        )

    def _first_extension_match(self, search_root: Path) -> Path | None:
        """Return the first file matching `{label}.*` in search_root, or None."""
        if not search_root.is_dir():
            return None
        matches = sorted(c for c in search_root.glob(f"{self._label}.*") if c.is_file())
        return matches[0] if matches else None

    def _canonical_domain_md(self, module_dir: Path, search_root: Path, domain_slug: str) -> Path:
        for root in (module_dir, search_root):
            for slug in _slug_variants(domain_slug):
                candidate = root / f"{slug}.md"
                if candidate.is_file():
                    return candidate
        return module_dir / f"{domain_slug}.md"

    def _locate_templates(self, module_dir: Path, domain_slug: str, active_format: str | None) -> AssetLocation:
        stems = self._template_stems(domain_slug)
        located = self._locate_in_shared_templates(module_dir, stems, active_format, domain_slug)
        if located is not None:
            return located
        located = self._locate_in_format_dir(module_dir, stems, active_format, domain_slug)
        if located is not None:
            return located
        located = self._locate_by_stem_glob(module_dir, stems, domain_slug)
        if located is not None:
            return located
        relative = _path_for_templates(module_dir, domain_slug, active_format)
        return AssetLocation("file", module_dir, domain_slug, path=(module_dir / relative).resolve())

    def _template_stems(self, domain_slug: str) -> list[str]:
        return [
            f"{slug}-{suffix}"
            for slug in _slug_variants(domain_slug)
            for suffix in ("templates", "template")
        ]

    def _locate_in_shared_templates(
        self, module_dir: Path, stems: list[str], active_format: str | None, domain_slug: str
    ) -> AssetLocation | None:
        shared = module_dir / "templates"
        if not shared.is_dir():
            return None
        ext = _FORMAT_TEMPLATE_EXT.get(active_format or "", "")
        if ext:
            for stem in stems:
                path = shared / f"{stem}{ext}"
                if path.is_file():
                    return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
        if active_format:
            alias = _FORMAT_DIR_ALIAS.get(active_format, active_format)
            format_folder = shared / alias
            if format_folder.is_dir():
                fidelity = _active_resource(self._host, "fidelity")
                return AssetLocation(
                    "folder",
                    module_dir,
                    domain_slug,
                    folder=format_folder.resolve(),
                    fidelity=fidelity,
                )
            return None
        return AssetLocation("folder", module_dir, domain_slug, folder=shared.resolve())

    def _locate_in_format_dir(
        self, module_dir: Path, stems: list[str], active_format: str | None, domain_slug: str
    ) -> AssetLocation | None:
        if not active_format:
            return None
        format_dir = module_dir / "formats" / active_format
        if not format_dir.is_dir():
            return None
        for stem in stems:
            for path in sorted(format_dir.glob(f"{stem}.*")):
                return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
        return None

    def _locate_by_stem_glob(
        self, module_dir: Path, stems: list[str], domain_slug: str
    ) -> AssetLocation | None:
        for stem in stems:
            for path in sorted(module_dir.glob(f"{stem}.*")):
                return AssetLocation("file", module_dir, domain_slug, path=path.resolve())
        return None


def _frontmatter_values(content: str, key: str) -> list[str]:
    """Read a YAML list or scalar for `key` from a leading --- frontmatter block."""
    if not content.startswith("---"):
        return []
    end = content.find("\n---", 3)
    if end < 0:
        return []
    block = content[3:end]
    prefix = f"{key}:"
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line.startswith(prefix):
            continue
        rest = line[len(prefix) :].strip()
        rest = rest.strip("[]")
        return [part.strip().strip("'\"") for part in rest.split(",") if part.strip()]
    return []


def keep_template_file(rel: str, content: str, fidelity: str | None) -> bool:
    """Whether a templates/ file belongs in the merged blob for this fidelity.

    No fidelity → keep everything (same as a whole-folder merge). Never keep
    stories-sketch on a format-filtered pack. story_map keeps story-map +
    thin-slice plus files whose frontmatter artifact is clearly story-map.
    """
    if not fidelity:
        return True
    stem = Path(rel).stem.lower()
    if stem.endswith("-sketch"):
        return False
    stems = _FIDELITY_TEMPLATE_STEMS.get(fidelity)
    if stems is None:
        return True
    if stem in stems:
        return True
    artifacts = _frontmatter_values(content, "artifact")
    allowed = _FIDELITY_TEMPLATE_ARTIFACTS.get(fidelity, frozenset())
    for art in artifacts:
        if art.replace("_", "-") in allowed:
            return True
    return False


class Asset:
    def __init__(self, location: AssetLocation) -> None:
        self._location = location

    @property
    def location(self) -> AssetLocation:
        return self._location

    @property
    def fidelity(self) -> str | None:
        return self._location.fidelity

    @property
    def format(self) -> str | None:
        return self._location.format

    def collect(self) -> str:
        from .markdown_extractor import _extract_single, thin_contexts_for_fidelity

        text = _extract_single(self._location)
        if self._location.label == "contexts":
            return thin_contexts_for_fidelity(text, self.fidelity)
        return text


class AssetCollection:
    def __init__(self, location: AssetLocation) -> None:
        self._location = location
        self.collection: dict[str, str] = {}

    @property
    def location(self) -> AssetLocation:
        return self._location

    @property
    def fidelity(self) -> str | None:
        return self._location.fidelity

    @property
    def format(self) -> str | None:
        return self._location.format

    def collect(self) -> dict[str, str]:
        from .markdown_extractor import (
            _extract_collection,
            thin_examples_by_fidelity,
            thin_examples_by_format,
        )

        items = _extract_collection(self._location)
        if self._location.label == "examples":
            items = thin_examples_by_format(items, self.format)
            items = thin_examples_by_fidelity(items, self.fidelity)
        self.collection = items
        return self.collection

    def merged(self) -> str:
        from .markdown_extractor import _merge_collection

        if not self.collection:
            self.collect()
        return _merge_collection(self.collection)
