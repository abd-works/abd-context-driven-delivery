"""Numbered versions of a design canvas: ``version-1``, ``version-2``, … beside each other under one folder, the release's
``.sessions/<release>/design-canvas``.

People edit a published canvas directly, so a regeneration never writes over one: it starts the next version, a
copy of the latest that the generator then renders into, and that version is published as a new canvas.
``versions.json`` remembers each version's published link, in the order they were published. A version kept as a
release is renamed to the release's name (``release``); numbering then starts again at ``version-1``, copied from
that release.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from space.work_state import DESIGN_CANVAS_FOLDER, WorkState

_VERSION = re.compile(r"^version-(\d+)$")


class PublishedVersion(Exception):
    """A generator tried to write into a version that is already published, where people may have edited it."""


class CanvasVersions:
    """The versions of the canvas kept under *root* (for example ``.sessions/<release>/design-canvas``)."""

    record_name = "versions.json"

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @classmethod
    def from_release(cls, repo_root: str | Path, release: str = "") -> CanvasVersions:
        """The canvas of *release* in the checkout at *repo_root*; the release being worked on when none is named."""
        return cls(WorkState(repo_root).release_folder(release) / DESIGN_CANVAS_FOLDER)

    @property
    def numbers(self) -> List[int]:
        if not self.root.is_dir():
            return []
        found = (_VERSION.match(path.name) for path in self.root.iterdir() if path.is_dir())
        return sorted(int(match.group(1)) for match in found if match)

    @property
    def latest(self) -> int:
        """The newest version, or 0 when there is none yet."""
        return self.numbers[-1] if self.numbers else 0

    def folder(self, number: int) -> Path:
        """The version's folder: it holds ``project/`` exactly as the canvas publishes it."""
        return self.root / f"version-{number}"

    def start_next(self) -> int:
        """Begin the next version as a copy of the latest (screens, images, fixtures), leaving the latest untouched."""
        number = self.latest + 1
        target = self.folder(number)
        base = self.folder(self.latest) if self.latest else self.latest_release()
        if base is not None:
            shutil.copytree(base, target)
        else:
            target.mkdir(parents=True)
        return number

    def latest_release(self) -> Optional[Path]:
        """The folder of the newest release (a published version renamed to its release's name), or None."""
        released = [self.root / name for name in self.links() if not _VERSION.match(name) and (self.root / name).is_dir()]
        return released[-1] if released else None

    def release(self, number: int, name: str) -> Path:
        """Keep a published version as the release *name*: its folder and its link take the release's name."""
        target = self.root / name
        self.folder(number).rename(target)
        links = {(name if key == self.folder(number).name else key): url for key, url in self.links().items()}
        self._write(links)
        return target

    def working(self) -> int:
        """The version a generator writes into: the latest while it is unpublished (no one has edited it yet),
        else a new one started from it."""
        if self.latest and self.link(self.latest) is None:
            return self.latest
        return self.start_next()

    def unpublished(self) -> int:
        """The latest version, for a generator that only adds to the version being prepared; a published version
        is people's canvas, so this refuses it."""
        if not self.latest or self.link(self.latest) is not None:
            raise PublishedVersion(f"version-{self.latest} is published; start the next version before generating into it")
        return self.latest

    def title(self, number: int, name: str) -> str:
        return f"{name} — version-{number}"

    def links(self) -> Dict[str, str]:
        """Each published version's canvas link, by version folder name."""
        record = self.root / self.record_name
        return json.loads(record.read_text(encoding="utf-8")) if record.is_file() else {}

    def link(self, number: int) -> Optional[str]:
        return self.links().get(self.folder(number).name)

    def record_link(self, number: int, url: str) -> None:
        links = self.links()
        links[self.folder(number).name] = url
        self._write(links)

    def _write(self, links: Dict[str, str]) -> None:
        (self.root / self.record_name).write_text(json.dumps(links, indent=1), encoding="utf-8")
