"""Spec support: git repositories a spec builds once for its process and copies for each example."""
from __future__ import annotations

import atexit
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path


class BuiltOnce:
    """A folder of git repositories, such as a clone and the bare origin it pushes to, built the first time an example
    asks for it and copied for every example after. Starting git a dozen times to build one takes half a second, and
    copying the folder a twentieth of that, while every example still gets repositories of its own to change.

    A clone names its origin by its absolute path, so each copy's git ``config`` files name the copy's own origin."""

    def __init__(self, prefix: str, build: Callable[[Path], object]) -> None:
        self._prefix = prefix
        self._build = build
        self._built: Path | None = None

    def copy(self) -> Path:
        """A new folder holding a copy of the repositories, for one example to change and remove."""
        built = self._built_folder()
        top = Path(tempfile.mkdtemp(prefix=self._prefix)).resolve()
        shutil.copytree(built, top, dirs_exist_ok=True)
        for config in top.rglob("config"):
            if config.parent.name == ".git" or (config.parent / "HEAD").is_file():
                self._repoint(config, built, top)
        return top

    def _built_folder(self) -> Path:
        if self._built is None:
            built = Path(tempfile.mkdtemp(prefix=self._prefix)).resolve()
            self._build(built)
            self._built = built
            atexit.register(shutil.rmtree, built, True)
        return self._built

    def _repoint(self, config: Path, built: Path, top: Path) -> None:
        """Name the copy in config wherever it names the built folder: as git escapes a Windows path in its config
        (``C:\\\\Users``), as the path itself, or with forward slashes."""
        text = config.read_text(encoding="utf-8")
        for spelling, copied in (
            (str(built).replace("\\", "\\\\"), str(top).replace("\\", "\\\\")),
            (str(built), str(top)),
            (built.as_posix(), top.as_posix()),
        ):
            text = text.replace(spelling, copied)
        if built.name in text:
            raise ValueError(f"{config} still names {built}, so this copy would change the repositories it was copied from")
        config.write_text(text, encoding="utf-8")
