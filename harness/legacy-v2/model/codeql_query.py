"""Workspace file walk. Story and class facts come from CodeQL queries, not a source scanner."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "__pycache__", ".codeql", ".kilo"}


def walk_files(root: Path) -> Iterable[Path]:
    """Files under root, skipping hidden folders and dependencies. A missing directory does not stop the walk."""
    stack = [Path(root)]
    while stack:
        folder = stack.pop()
        try:
            children = list(folder.iterdir())
        except OSError:
            continue
        for path in children:
            name = path.name
            if name.startswith(".") or name in _SKIP_DIRS:
                continue
            try:
                is_dir = path.is_dir()
            except OSError:
                continue
            if is_dir:
                stack.append(path)
                continue
            yield path
