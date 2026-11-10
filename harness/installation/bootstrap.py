"""Catalog import bootstrap for CLI, probes, and tests — same paths as the MCP host."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_import_path(repo: Path | str | None = None) -> Path:
    """Add repo root and ``cdd_guidance/actions`` (etc.) so ``from validate.validate`` works."""
    from harness.installation.installer import Installer

    root = Path(repo).resolve() if repo is not None else repo_root()
    Installer(repo=root).ensure_import_path(root)
    return root
