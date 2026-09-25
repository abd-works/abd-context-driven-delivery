"""Write transformer render output under a fixture temp folder for inspection."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from practices.bdd.model.transformation.bdd_transformer import BddTransformer
from practices.clean_engineering.model.transformation.clean_engineering_transformer import (
    CleanEngineeringTransformer,
)
from practices.stories.model.transformation.story_map_transformer import StoryMapTransformer


def write_temp(nodes: list, dest: Path) -> None:
    target = _native(dest)
    if target.exists():
        _clear_readonly(target)
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for node in nodes:
        files = node.render("logical")
        folder = dest / _label(node)
        for relative, text in files.items():
            _write(folder / relative, text)


def _label(node) -> str:
    if isinstance(node, StoryMapTransformer):
        return "stories"
    if isinstance(node, CleanEngineeringTransformer):
        return "ce"
    if isinstance(node, BddTransformer):
        return "bdd"
    return type(node).__name__


def _write(path: Path, text: str) -> None:
    native = _native(path)
    native.parent.mkdir(parents=True, exist_ok=True)
    native.write_text(text, encoding="utf-8")


def _clear_readonly(path: Path) -> None:
    for current, dirs, files in os.walk(path):
        for name in dirs + files:
            child = Path(current) / name
            child.chmod(child.stat().st_mode | 0o222)
    path.chmod(path.stat().st_mode | 0o222)


def _native(path: Path) -> Path:
    text = str(path.resolve())
    if os.name == "nt" and not text.startswith("\\\\?\\"):
        return Path("\\\\?\\" + text)
    return path
