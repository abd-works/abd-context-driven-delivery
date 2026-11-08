"""Folders a working-copy scan never enters: build output, test-run output, caches, dot-folders, and the example and
fixture folders that hold deliberately faulty or throwaway source.

An `_examples` folder holds each rule's faulty and repaired example, and a `fixtures` folder holds test input; read as
the project's own code, their faults are reported as the project's. The rule specs copy an example into a folder of its
own before they read it. `.examples*` folders hold example source the practices read, so they are scanned like any
other folder.
"""

from __future__ import annotations

import os
from pathlib import Path

SKIPPED_FOLDERS = frozenset(
    {
        ".codeql",
        ".git",
        "node_modules",
        "__pycache__",
        ".sessions",
        "retired",
        ".context",
        ".venv",
        "dist",
        "build",
        "coverage",
        ".next",
        "out",
        "playwright-report",
        "test-results",
        ".cursor",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "htmlcov",
        "_examples",
        "fixtures",
    }
)


def skips_folder(name: str) -> bool:
    """True for a build, test-run, or cache folder, and for a dot-folder other than `.examples*`."""
    if name in SKIPPED_FOLDERS:
        return True
    return name.startswith(".") and not name.startswith(".examples")


def scanned_files(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    """Every file under ``root`` outside skipped folders, sorted; only ``suffixes`` when given."""
    found: list[Path] = []
    if not root.is_dir():
        return found
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not skips_folder(name)]
        found.extend(
            Path(dirpath) / name
            for name in filenames
            if suffixes is None or Path(name).suffix.lower() in suffixes
        )
    return sorted(found)
