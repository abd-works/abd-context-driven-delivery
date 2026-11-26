"""Where each file a canvas version's screens load comes from (*ScreenSources*), kept in the version's
``project/screen-sources.json``.

The render copies the files a screen's markup needs into the version (``each-version-carries-its-files``), bundles
the production views it mounts, and builds the fixtures bundle from the story code. Each copy forgets where it came
from, so the render records it: the path the copy takes in the project folder, and the file or folder it was copied,
converted or built from, named from the project's root. A converted copy (*ContainerCss*) is recorded under its
source, since it is that file with its sizes read from the screen's frame. The UX rule ``screen-files-from-production``
reads this record to trace every file a screen loads back to the product's own code.

See ``story_canvas.md`` beside this file, *Prototype screens*."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping, Optional

SOURCES_FILE = "screen-sources.json"
# What a recorded file is: a copy of the product's code or the prototype's, or the fixtures bundle built from the
# story code.
COPY = "copy"
FIXTURES = "fixtures"


class ScreenSources:
    """The record of where the files in one canvas version's *project* folder come from."""

    def __init__(self, project: Path) -> None:
        self.project = Path(project)

    @property
    def file(self) -> Path:
        return self.project / SOURCES_FILE

    @property
    def entries(self) -> dict[str, dict]:
        """Each recorded path in the project folder, with where it comes from (``from``, from the project's root) and
        what it is (``kind``)."""
        if not self.file.is_file():
            return {}
        try:
            held = json.loads(self.file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
        return {path: entry for path, entry in held.items() if isinstance(entry, dict)}

    def record(self, sources: Mapping[str, Path], project_root: Path, kind: str = COPY) -> None:
        """Keep, over what is recorded, where each path in sources (a path in the project folder) comes from."""
        held = self.entries
        for path, source in sources.items():
            held[Path(path).as_posix()] = {"from": _from_root(Path(source), Path(project_root)), "kind": kind}
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(dict(sorted(held.items())), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def origin(self, path: str) -> Optional[dict]:
        """Where the file at path (in the project folder) comes from: the record of the path itself, else of the
        nearest folder holding it; none when nothing recorded names it."""
        entries = self.entries
        held = [recorded for recorded in entries if path == recorded or path.startswith(recorded.rstrip("/") + "/")]
        return entries[max(held, key=len)] if held else None


def _from_root(source: Path, project_root: Path) -> str:
    """source named from the project's root, or absolute when it lies outside the project."""
    resolved, root = source.resolve(), project_root.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return Path(os.path.abspath(resolved)).as_posix()
