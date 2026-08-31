"""Repo category dirs for ``python -m tools`` — this checkout, not another clone."""

from __future__ import annotations

import sys
from pathlib import Path

CATEGORY_DIRS = (
    "primitives",
    "utilities",
    "context_tools",
    "context_tools/actions",
    "agents",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def pythonpath_entries(root: Path | None = None) -> list[str]:
    root = (root or repo_root()).resolve()
    return [str(root)] + [str(root / name) for name in CATEGORY_DIRS]


def prepend_sys_path(root: Path | None = None) -> None:
    for entry in reversed(pythonpath_entries(root)):
        if entry not in sys.path:
            sys.path.insert(0, entry)


def write_venv_pth(venv_dir: Path, root: Path | None = None) -> Path:
    """Write ``abd_cdd_paths.pth`` so site import uses *this* repo."""
    path = Path(venv_dir) / "abd_cdd_paths.pth"
    path.write_text("\n".join(pythonpath_entries(root)) + "\n", encoding="utf-8")
    return path


def tools_package_is_from(root: Path | None = None) -> bool:
    import tools

    root = (root or repo_root()).resolve()
    return Path(tools.__file__).resolve().is_relative_to(root)


def repo_python(root: Path | None = None) -> str:
    """Prefer this checkout's venv Python for subprocess ``python -m tools`` calls."""
    root = (root or repo_root()).resolve()
    for candidate in (
        root / ".venv" / "Scripts" / "python.exe",
        root / "venv" / "Scripts" / "python.exe",
        root / ".venv" / "bin" / "python",
        root / "venv" / "bin" / "python",
    ):
        if candidate.is_file():
            return str(candidate)
    return sys.executable
