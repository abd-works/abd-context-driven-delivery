"""Which scanner scripts apply to a skill (rules frontmatter + ``scanners/*-scanner.py``).

Used by **execute-skill-using-skills-rules** ``run_scanners.py``, ``rule_inventory.py --list-scanners``, and **build_skill**
``build_pipeline_plan.py``. ``scripts/base/build.py`` inlines the same logic so scaffolded skill packages
stay self-contained without a separate ``scanner_paths`` module under ``scripts/base/``.

Language-specific scanners
--------------------------
Pass ``language="python"`` (or ``"javascript"``, etc.) to look inside ``scanners/<language>/``
instead of ``scanners/`` directly.  Rule frontmatter stays the same plain stem regardless of
language — only the lookup path changes:

    scanner: orchestrator_pattern_scanner.py   # resolves to scanners/python/ when --language python

Without ``language`` the old flat ``scanners/`` layout is used (backward compatible).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def skill_build_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    """Return the ``build`` block from ``skill-config.json`` (empty dict if missing)."""
    b = cfg.get("build")
    return b if isinstance(b, dict) else {}


def _parse_frontmatter_scanner(content: str) -> str | None:
    text = content.lstrip("\ufeff")
    match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    for line in match.group(1).split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        if k.strip().lower() == "scanner":
            return v.strip().strip('"').strip("'") or None
    return None


def _resolve_scanner_value(
    skill_root: Path, raw: str, language: str | None = None
) -> str | None:
    """Map ``scanner:`` frontmatter to a relative path under ``scanners/``.

    Resolution order (first match wins):
    1. ``scanners/<language>/<filename>``  — when ``language`` is given
    2. ``scanners/<filename>``             — flat layout (backward compat)

    ``<filename>`` is derived from ``raw``:
    - ends with ``.py``      → used as-is
    - ends with ``-scanner`` → ``{raw}.py``
    - otherwise              → ``{raw}-scanner.py``

    Rejects values containing path separators or ``..`` to prevent traversal.
    """
    v = raw.strip().strip('"').strip("'")
    if not v or ".." in v or "\\" in v:
        return None
    # Allow a single "language/stem" slash written explicitly in the frontmatter
    # (treated the same as language parameter; only one level of nesting permitted).
    if "/" in v:
        parts = v.split("/", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return None
        explicit_lang, stem = parts[0], parts[1]
        return _resolve_scanner_value(skill_root, stem, language=explicit_lang)

    name = v
    if name.endswith(".py"):
        filename = name
    elif name.endswith("-scanner"):
        filename = f"{name}.py"
    else:
        filename = f"{name}-scanner.py"

    # Language-specific subfolder (preferred)
    if language:
        candidate = skill_root / "scanners" / language / filename
        if candidate.is_file():
            return f"scanners/{language}/{filename}"

    # Flat layout fallback
    candidate = skill_root / "scanners" / filename
    if candidate.is_file():
        return f"scanners/{filename}"

    return None


def scanners_from_rule_frontmatter(
    skill_root: Path, language: str | None = None
) -> list[str]:
    """Paths under ``scanners/`` from ``scanner:`` in each ``rules/*.md`` (sorted by filename).

    When ``language`` is provided, resolution prefers ``scanners/<language>/`` first.
    """
    rules_dir = skill_root / "rules"
    if not rules_dir.is_dir():
        return []
    out: list[str] = []
    seen: set[str] = set()
    for md in sorted(rules_dir.glob("*.md")):
        if md.name == "README.md":
            continue
        spec = _parse_frontmatter_scanner(md.read_text(encoding="utf-8"))
        if not spec:
            continue
        rel = _resolve_scanner_value(skill_root, spec, language=language)
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def discover_scanner_scripts(
    skill_root: Path, language: str | None = None
) -> list[str]:
    """Sorted relative POSIX paths for ``*-scanner.py`` entrypoints.

    When ``language`` is provided, scans ``scanners/<language>/*-scanner.py``.
    Otherwise scans the flat ``scanners/*-scanner.py`` layout (backward compat).
    Modules that do not end in ``-scanner.py`` are excluded (they are helpers/bases).
    """
    base = skill_root / "scanners" / language if language else skill_root / "scanners"
    if not base.is_dir():
        return []
    out: list[str] = []
    for p in sorted(base.glob("*-scanner.py")):
        if not p.is_file():
            continue
        out.append(str(p.relative_to(skill_root)).replace("\\", "/"))
    return out


def list_scanner_scripts(
    skill_root: Path, cfg: dict[str, Any], language: str | None = None
) -> list[str]:
    """Return scanner script paths to run: rule ``scanner:`` first, then any other ``*-scanner.py``.

    ``cfg`` is reserved for API compatibility.
    ``language`` (e.g. ``"python"``, ``"javascript"``) restricts lookup to ``scanners/<language>/``.
    Without ``language``, the flat ``scanners/`` layout is used (backward compatible).
    """
    del cfg  # API compatibility only
    seen: set[str] = set()
    ordered: list[str] = []

    def add(rel: str | None) -> None:
        if not rel:
            return
        s = str(rel).replace("\\", "/")
        if s not in seen:
            seen.add(s)
            ordered.append(s)

    for rel in scanners_from_rule_frontmatter(skill_root, language=language):
        add(rel)

    for rel in discover_scanner_scripts(skill_root, language=language):
        add(rel)

    return ordered


# Backward-compatible name for older call sites
merge_scanner_paths = list_scanner_scripts


def resolve_build_pipeline(skill_root: Path, cfg: dict[str, Any]) -> list[str]:
    """If ``build.build_pipeline`` is non-empty, return that; else :func:`list_scanner_scripts`."""
    build_cfg = skill_build_cfg(cfg)
    raw = build_cfg.get("build_pipeline")
    if raw:
        return [str(x).replace("\\", "/") for x in raw]
    return list_scanner_scripts(skill_root, cfg)
