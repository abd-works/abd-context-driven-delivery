from __future__ import annotations

from pathlib import Path
from typing import Any


def path_for_name(module_dir: Path, name: str) -> str:
    folder = module_dir / name
    if folder.is_dir():
        return f"{name}/"
    if (module_dir / name).is_file():
        return name
    if (module_dir / f"{name}.md").is_file():
        return name
    return "\u00a7 " + name.title()


def _slug_variants(domain_slug: str) -> list[str]:
    """toolset_name is snake_case; on-disk domain files often use hyphens."""
    variants = [domain_slug]
    for alt in (domain_slug.replace("_", "-"), domain_slug.replace("-", "_")):
        if alt not in variants:
            variants.append(alt)
    return variants


def path_for_templates(module_dir: Path, domain_slug: str, active_format: str | None) -> str:
    """Relative path hint for the domain artifact templates file or folder."""
    shared = module_dir / "templates"
    if shared.is_dir():
        for slug in _slug_variants(domain_slug):
            for stem in (f"{slug}-templates", f"{slug}-template"):
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
path_for_template = path_for_templates


def format_keys(module_dir: Path) -> list[str]:
    formats_dir = module_dir / "formats"
    if not formats_dir.is_dir():
        return []
    md_stems = sorted(p.stem for p in formats_dir.glob("*.md") if p.is_file())
    if md_stems:
        return md_stems
    return sorted(p.name for p in formats_dir.iterdir() if p.is_dir())


def active_resource(instance: Any, key: str | None) -> str | None:
    if not key:
        return None
    value = getattr(instance, key, None)
    return str(value) if value else None
