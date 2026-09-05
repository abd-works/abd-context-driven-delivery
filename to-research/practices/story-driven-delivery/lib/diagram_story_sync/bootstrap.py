"""Resolve sibling skill ``scripts`` directories onto ``sys.path``.

The diagram-story-sync ecosystem assumes a family package layout::

    story-driven-delivery/
        lib/diagram_story_sync/         <- this package
        skills/story-graph-ops/scripts/ <- canonical story_graph_ops
        skills/drawio-story-sync/scripts/
        skills/miro-story-sync/scripts/

Deployed engagement layout::

    .cursor/
        lib/diagram_story_sync/
        skills/story-graph-ops/scripts/
        skills/<backend>/scripts/
"""
from __future__ import annotations

import sys
from pathlib import Path


def _lib_root() -> Path:
    """Directory containing ``diagram_story_sync`` (``lib/``)."""
    return Path(__file__).resolve().parents[1]


def _package_root() -> Path:
    """Family package root (``story-driven-delivery/`` or ``.cursor/``)."""
    return _lib_root().parent


def ensure_common_on_path() -> None:
    """Insert ``lib/`` so ``import diagram_story_sync`` works from any caller."""
    p = str(_lib_root())
    if p not in sys.path:
        sys.path.insert(0, p)


def ensure_story_graph_ops_on_path() -> None:
    """Insert sibling ``skills/story-graph-ops/scripts`` if present."""
    ops_scripts = _package_root() / "skills" / "story-graph-ops" / "scripts"
    p = str(ops_scripts)
    if ops_scripts.is_dir() and p not in sys.path:
        sys.path.insert(0, p)


def ensure_backend_paths(backend_skill_dir: Path) -> None:
    """Insert ``lib/`` plus a backend skill's ``scripts/`` and ``story-graph-ops``."""
    ensure_common_on_path()
    ensure_story_graph_ops_on_path()
    scripts = backend_skill_dir / "scripts"
    p = str(scripts)
    if scripts.is_dir() and p not in sys.path:
        sys.path.insert(0, p)


ensure_common_on_path()
ensure_story_graph_ops_on_path()
