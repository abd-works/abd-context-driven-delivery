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


def path_for_template(module_dir: Path, domain_slug: str, active_format: str | None) -> str:
    template_stem = f"{domain_slug}-template"
    if active_format:
        format_dir = module_dir / "formats" / active_format
        if format_dir.is_dir():
            for path in sorted(format_dir.glob(f"{template_stem}.*")):
                return path.relative_to(module_dir).as_posix()
            return f"formats/{active_format}/{template_stem}"
    for path in sorted(module_dir.glob(f"{template_stem}.*")):
        return path.name
    return template_stem


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
