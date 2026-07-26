"""Instruction values, path routing, and @instruction slots."""
from __future__ import annotations

import functools
import inspect
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeAlias, TypeVar

# Host that carries module_dir / domain_slug for instruction and declaration routing.
InstructionHost: TypeAlias = Any

F = TypeVar("F", bound=Callable[..., Any])


def _section_heading_for_name(name: str) -> str:
    """Snake/kebab tool names → markdown section titles (``create_session`` → ``Create Session``)."""
    return name.replace("_", " ").replace("-", " ").title()


def _heading_in_markdown(md_path: Path, heading: str) -> bool:
    pattern = re.compile(
        rf"^#{{1,6}}\s+{re.escape(heading)}\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    return pattern.search(md_path.read_text(encoding="utf-8")) is not None


def _path_for_name(module_dir: Path, name: str) -> str:
    folder = module_dir / name
    if folder.is_dir():
        return f"{name}/"
    if (module_dir / name).is_file():
        return name
    if (module_dir / f"{name}.md").is_file():
        return name
    heading = _section_heading_for_name(name)
    # Section in kit ``{folder}.md`` (sessions.md, …) — § form uses domain_slug = folder name.
    kit_md = _kit_markdown(module_dir)
    if kit_md is not None and _heading_in_markdown(kit_md, heading):
        return "\u00a7 " + heading
    # Flat module beside its md (base/base_context_tool.py → base_context_tool.md).
    for md_path in sorted(module_dir.glob("*.md")):
        if _heading_in_markdown(md_path, heading):
            return f"{md_path.stem} \u00a7 {heading}"
    return "\u00a7 " + heading


def _slug_variants(domain_slug: str) -> list[str]:
    """toolset_name is snake_case; on-disk domain files often use hyphens."""
    variants = [domain_slug]
    for alt in (domain_slug.replace("_", "-"), domain_slug.replace("-", "_")):
        if alt not in variants:
            variants.append(alt)
    return variants


_FORMAT_TEMPLATE_EXT = {
    "python": ".py",
    "javascript": ".js",
    "markdown": ".md",
    "typescript": ".ts",
    "java": ".java",
}


def _path_for_templates(module_dir: Path, domain_slug: str, active_format: str | None) -> str:
    """Relative path hint for the domain artifact templates file or folder."""
    shared = module_dir / "templates"
    if shared.is_dir():
        ext = _FORMAT_TEMPLATE_EXT.get(active_format or "", "")
        for slug in _slug_variants(domain_slug):
            for stem in (f"{slug}-templates", f"{slug}-template"):
                if ext:
                    preferred = shared / f"{stem}{ext}"
                    if preferred.is_file():
                        return preferred.relative_to(module_dir).as_posix()
                for path in sorted(shared.glob(f"{stem}.*")):
                    return path.relative_to(module_dir).as_posix()
        return "templates"
    for slug in _slug_variants(domain_slug):
        for stem in (f"{slug}-templates", f"{slug}-template"):
            if active_format:
                format_dir = module_dir / "formats" / active_format
                if format_dir.is_dir():
                    for path in sorted(format_dir.glob(f"{stem}.*")):
                        return path.relative_to(module_dir).as_posix()
            for path in sorted(module_dir.glob(f"{stem}.*")):
                return path.name
    primary = _slug_variants(domain_slug)[0]
    if active_format:
        return f"formats/{active_format}/{primary}-templates"
    return f"{primary}-templates"


# Back-compat alias
_path_for_template = _path_for_templates


def _format_keys(module_dir: Path) -> list[str]:
    formats_dir = module_dir / "formats"
    if not formats_dir.is_dir():
        return []
    md_stems = sorted(p.stem for p in formats_dir.glob("*.md") if p.is_file())
    if md_stems:
        return md_stems
    return sorted(p.name for p in formats_dir.iterdir() if p.is_dir())


def _active_resource(instance: Any, key: str | None) -> str | None:
    if not key:
        return None
    value = getattr(instance, key, None)
    return str(value) if value else None


class Instruction:
    def __init__(self, text: str, module_dir: Path, *, domain_slug: str | None = None) -> None:
        self.text = text.strip()
        self.module_dir = Path(module_dir)
        self.domain_slug = domain_slug or self.module_dir.name
        self._host: InstructionHost | None = None
        self._label: str | None = None
        self._collection = False
        self._group: str | None = None
        self._filter_key: str | None = None

    @classmethod
    def ref(
        cls,
        host: InstructionHost,
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
        from primitives.assets import AssetCollection, AssetLocation
        from primitives.assets.markdown_extractor import _read_file, _read_section

        if self._label is not None and self._host is not None:
            return self._expand_ref()
        if not self.matches_file_or_folder():
            return self.text
        path_part, section = self._split_section()
        if path_part.startswith("§"):
            section = path_part.removeprefix("§").strip()
            path = self._canonical_markdown()
            if not path.is_file():
                return ""
            if section:
                from primitives.assets.markdown_extractor import _section_exists

                if not _section_exists(path, section):
                    return ""
                return _read_section(path, section)
            return _read_file(path)
        resolved = self._resolve_path(path_part)
        if resolved.is_dir():
            location = AssetLocation(
                "folder", self.module_dir, self.domain_slug, folder=resolved.resolve()
            )
            return AssetCollection(location).merged()
        if resolved.is_file():
            return _read_section(resolved, section) if section else _read_file(resolved)
        candidate = Path(f"{resolved}.md")
        if candidate.is_file():
            return _read_section(candidate, section) if section else _read_file(candidate)
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
        from primitives.assets import Asset, AssetCollection, AssetLocator

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


def instruction(
    func: F | None = None,
    *,
    collection: bool = False,
    group: str | None = None,
    filter_key: str | None = None,
    override: bool = False,
    label: str | None = None,
) -> F | Callable[[F], F]:
    def decorate(target: F) -> F:
        resolved_label = label or target.__name__

        if override:
            wrapped = target
        else:
            @functools.wraps(target)
            def wrapped(instance: Any) -> Any:
                # Read attrs at call time so @focus (applied outside) can set them.
                return Instruction.ref(
                    instance,
                    getattr(wrapped, "_instruction_label", resolved_label),
                    collection=getattr(wrapped, "_instruction_collection", collection),
                    group=getattr(wrapped, "_instruction_group", group),
                    filter_key=getattr(wrapped, "_instruction_filter_key", filter_key),
                )

        wrapped._is_instruction_slot = True  # type: ignore[attr-defined]
        wrapped._instruction_label = resolved_label  # type: ignore[attr-defined]
        wrapped._instruction_collection = collection  # type: ignore[attr-defined]
        wrapped._instruction_group = group  # type: ignore[attr-defined]
        wrapped._instruction_filter_key = filter_key  # type: ignore[attr-defined]
        return wrapped  # type: ignore[return-value]

    if func is not None:
        return decorate(func)
    return decorate


def instruction_slot_names(toolset_cls: type) -> frozenset[str]:
    names: set[str] = set()
    for cls in toolset_cls.__mro__:
        if cls is object:
            continue
        for name, member in cls.__dict__.items():
            if callable(member) and getattr(member, "_is_instruction_slot", False):
                names.add(name)
    return frozenset(names)


def _instruction_slot_for(toolset_cls: type, name: str) -> Callable[..., Any] | None:
    for cls in toolset_cls.__mro__:
        if cls is object:
            continue
        member = cls.__dict__.get(name)
        if member is not None and callable(member) and getattr(member, "_is_instruction_slot", False):
            return member
    return None


def _defining_module_dir(action_func: Any) -> Path:
    return Path(inspect.getfile(action_func)).resolve().parent


_FRAMEWORK_ACTIONS = frozenset(
    {
        "generate",
        "validate",
        "satisfy",
        "repair",
        "scan",
        "partition",
        "index",
        "segment",
        "document",
        "log_fix",
    }
)


def _is_framework_action(action_name: str) -> bool:
    return action_name in _FRAMEWORK_ACTIONS


def _kit_markdown(module_dir: Path) -> Path | None:
    """``{slug}.md`` beside a kit package (``sessions.md``, ``partition_pipeline.md``, …)."""
    for slug in _slug_variants(module_dir.name):
        candidate = module_dir / f"{slug}.md"
        if candidate.is_file():
            return candidate
    return None


def _section_from_markdown(md_path: Path, action_name: str) -> str | None:
    """Return section body from a markdown file when a matching ``#`` heading exists."""
    heading = _section_heading_for_name(action_name)
    if not _heading_in_markdown(md_path, heading):
        return None
    from primitives.assets.markdown_extractor import _read_section

    return _read_section(md_path, heading)


def _section_in_kit(module_dir: Path, action_name: str) -> str | None:
    """Return section body from kit slug.md or another ``*.md`` with that heading."""
    heading = _section_heading_for_name(action_name)
    kit_md = _kit_markdown(module_dir)
    if kit_md is not None:
        text = _section_from_markdown(kit_md, action_name)
        if text is not None:
            return text
    for md_path in sorted(module_dir.glob("*.md")):
        if kit_md is not None and md_path == kit_md:
            continue
        text = _section_from_markdown(md_path, action_name)
        if text is not None:
            return text
    return None


def _framework_action_prose(
    action_name: str,
    action_func: Any | None = None,
    *,
    instance: Any | None = None,
) -> str | None:
    """Load kit prose for an action: ``{action}.md`` or a section in kit ``{slug}.md``.

    Walks the instance MRO so a domain override still resolves kit prose.
    Flat modules also resolve ``{module_stem}.md`` beside the defining ``.py``.
    """
    locations: list[tuple[Path, Path | None]] = []
    if action_func is not None:
        try:
            py_file = Path(inspect.getfile(action_func)).resolve()
            locations.append((py_file.parent, py_file))
        except (TypeError, OSError):
            locations.append((_defining_module_dir(action_func), None))
    if instance is not None:
        for cls in type(instance).__mro__:
            member = cls.__dict__.get(action_name)
            if member is None:
                continue
            try:
                py_file = Path(inspect.getfile(member)).resolve()
                locations.append((py_file.parent, py_file))
            except (TypeError, OSError):
                continue
    seen: set[Path] = set()
    for module_dir, py_file in locations:
        if module_dir in seen:
            continue
        seen.add(module_dir)
        candidate = module_dir / f"{action_name}.md"
        if candidate.is_file():
            return Instruction(action_name, module_dir).expand()
        if py_file is not None:
            sibling = py_file.with_suffix(".md")
            if sibling.is_file():
                text = _section_from_markdown(sibling, action_name)
                if text is not None:
                    return text
        section_text = _section_in_kit(module_dir, action_name)
        if section_text is not None:
            return section_text
    return None


def _instruction_ref_resolves(instance: Any, label: str) -> bool:
    from primitives.assets import AssetLocator

    location = AssetLocator(instance, label).locate()
    if location.kind == "file" and location.path is not None and location.path.is_file():
        return True
    if location.kind == "folder" and location.folder is not None and location.folder.is_dir():
        return True
    if (
        location.kind == "section"
        and location.section_file is not None
        and location.section_file.is_file()
        and location.section_heading
    ):
        content = location.section_file.read_text(encoding="utf-8")
        pattern = re.compile(
            rf"^#{{1,6}}\s+{re.escape(location.section_heading)}\s*$",
            re.MULTILINE | re.IGNORECASE,
        )
        return pattern.search(content) is not None
    return False


def _expand_docstring(docstring: str, action_func: Any, *, instance: Any | None = None) -> str:
    text = docstring.strip()
    if not text:
        return text
    if text.startswith("§"):
        module_dir = _defining_module_dir(action_func)
        if instance is not None:
            module_dir = Path(getattr(instance, "module_dir", module_dir))
        return Instruction(text, module_dir).expand()
    if " " in text or "\n" in text:
        return text
    if (
        instance is not None
        and text in _FRAMEWORK_ACTIONS
        and getattr(type(instance), "_is_context", False)
    ):
        # Kit/base prose (defining action) plus domain ``{slug}.md`` § Action when present.
        # Replaces the old generate_instructions / document_instructions slots.
        parts: list[str] = []
        framework_text = _framework_action_prose(
            text, action_func, instance=instance
        )
        if framework_text:
            parts.append(framework_text)
        domain_dir = Path(getattr(instance, "module_dir", _defining_module_dir(action_func)))
        domain_text = _section_in_kit(domain_dir, text)
        if domain_text and domain_text not in parts:
            parts.append(domain_text)
        if parts:
            return "\n\n".join(parts)
    if instance is not None and _instruction_ref_resolves(instance, text):
        return Instruction.ref(instance, text).expand()
    defining_dir = _defining_module_dir(action_func)
    return Instruction(_path_for_name(defining_dir, text), defining_dir).expand()


def _inline(instance: Any, member: str) -> str:
    toolset_cls = type(instance)
    slot = _instruction_slot_for(toolset_cls, member)
    if slot is not None:
        result = slot(instance)
    else:
        result = getattr(instance, member)()
    if isinstance(result, Instruction):
        return result.expand()
    if isinstance(result, str):
        return result
    if result is None:
        return ""
    return str(result)
