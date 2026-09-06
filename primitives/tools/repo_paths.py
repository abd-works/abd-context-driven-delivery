"""Repo category dirs for ``python -m tools`` — this checkout, not another clone."""

from __future__ import annotations

import os
import sys
from pathlib import Path

CATEGORY_DIRS = ("primitives", "utilities", "context_tools", "context_tools/actions")
_PTH_NAME = "abd_cdd_paths.pth"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_source_paths(root: Path | None = None) -> list[Path]:
    root = (root or repo_root()).resolve()
    return [root] + [root / name for name in CATEGORY_DIRS]


def pythonpath_entries(root: Path | None = None) -> list[str]:
    return [str(path) for path in repo_source_paths(root)]


def _site_packages_dir(venv_dir: Path) -> Path:
    venv_dir = Path(venv_dir)
    for candidate in (
        venv_dir / "Lib" / "site-packages",
        venv_dir / "lib" / "site-packages",
    ):
        if candidate.is_dir():
            return candidate
    path = venv_dir / "Lib" / "site-packages"
    path.mkdir(parents=True, exist_ok=True)
    return path


def venv_pth_entries(venv_dir: Path, root: Path | None = None) -> list[str]:
    """Repo paths relative to ``Lib/site-packages`` for portable ``.pth`` files."""
    site_packages = _site_packages_dir(Path(venv_dir))
    return [
        Path(os.path.relpath(source, site_packages)).as_posix()
        for source in repo_source_paths(root)
    ]


def prepend_sys_path(root: Path | None = None) -> None:
    for entry in reversed(pythonpath_entries(root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)


def write_venv_pth(venv_dir: Path, root: Path | None = None) -> Path:
    """Write ``abd_cdd_paths.pth`` under site-packages so import uses *this* repo."""
    venv_dir = Path(venv_dir)
    path = _site_packages_dir(venv_dir) / _PTH_NAME
    path.write_text("\n".join(venv_pth_entries(venv_dir, root)) + "\n", encoding="utf-8")
    legacy = venv_dir / _PTH_NAME
    if legacy.is_file() and legacy != path:
        legacy.unlink()
    return path


def tools_package_is_from(root: Path | None = None) -> bool:
    import tools

    root = (root or repo_root()).resolve()
    return Path(tools.__file__).resolve().is_relative_to(root)
