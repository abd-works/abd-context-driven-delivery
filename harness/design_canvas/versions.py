"""Numbered versions of a design canvas: ``version-1``, ``version-2``, … beside each other under one folder, the
``design-canvas`` folder in the UX practice's root.

People edit a published canvas directly, so a regeneration never writes over one: it starts the next version, a
copy of the latest that the generator then renders into, and that version is published as a new canvas.
``versions.json`` remembers each version's published link, in the order they were published (*PublishedLinks*). A
version kept as a release is renamed to the release's name (``CanvasVersion.release``); numbering then starts again at
``version-1``, copied from that release.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import List, Optional

from harness.installation.json_file import JsonFile
from harness.installation.published_links import PublishedLinks

# The folder a canvas is kept in, under the UX practice's root, where the UX practice writes its other outputs.
DESIGN_CANVAS_FOLDER = "design-canvas"
_VERSION = re.compile(r"^version-(\d+)$")


class PublishedVersion(Exception):
    """A generator tried to write into a version that is already published, where people may have edited it."""


class CanvasVersion:
    """One version of a canvas: its folder, which holds ``project/`` exactly as the canvas publishes it, its number
    (none for a version kept as a release), and the link it was published at."""

    def __init__(self, folder: Path, published: PublishedLinks) -> None:
        self.folder = folder
        self._published = published

    @property
    def number(self) -> Optional[int]:
        """The version's number; none for a version kept as a release under its release's name."""
        found = _VERSION.match(self.folder.name)
        return int(found.group(1)) if found else None

    @property
    def link(self) -> Optional[str]:
        """The link the version was published at; none while it is unpublished."""
        return self._published.of(self.folder.name)

    def title(self, name: str) -> str:
        """The title the version is published under: the canvas's name and the version's folder."""
        return f"{name} — {self.folder.name}"

    def publish_at(self, url: str) -> None:
        """Keep url as the link the version was published at."""
        self._published.record(self.folder.name, url)

    def release(self, name: str) -> CanvasVersion:
        """Keep this published version as the release name: its folder and its link take the release's name."""
        target = self.folder.parent / name
        self.folder.rename(target)
        self._published.rename(self.folder.name, name)
        return CanvasVersion(target, self._published)


class CanvasVersions:
    """The versions of the canvas kept under root (for example ``<ux root>/design-canvas``)."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.published = PublishedLinks(JsonFile(self.root / "versions.json"))

    @classmethod
    def in_practice_root(cls, practice_root: str | Path) -> CanvasVersions:
        """The canvas the UX practice keeps in its root, the folder session.json names for it (``practices.ux.root``),
        beside its other outputs."""
        return cls(Path(practice_root) / DESIGN_CANVAS_FOLDER)

    @property
    def _numbers(self) -> List[int]:
        if not self.root.is_dir():
            return []
        found = (_VERSION.match(path.name) for path in self.root.iterdir() if path.is_dir())
        return sorted(int(match.group(1)) for match in found if match)

    def _numbered(self, number: int) -> CanvasVersion:
        return CanvasVersion(self.root / f"version-{number}", self.published)

    @property
    def latest(self) -> Optional[CanvasVersion]:
        """The newest numbered version; none when there is none yet."""
        numbers = self._numbers
        return self._numbered(numbers[-1]) if numbers else None

    def start_next(self) -> CanvasVersion:
        """Begin the next version as a copy of the latest (screens, images, fixtures), else of the newest release,
        leaving that one untouched."""
        latest = self.latest
        target = self._numbered((latest.number if latest is not None else 0) + 1)
        base = latest.folder if latest is not None else self._latest_release()
        if base is not None:
            shutil.copytree(base, target.folder)
        else:
            target.folder.mkdir(parents=True)
        return target

    def _latest_release(self) -> Optional[Path]:
        """The folder of the newest release (a published version renamed to its release's name), or None."""
        released = [self.root / name for name in self.published.all() if not _VERSION.match(name) and (self.root / name).is_dir()]
        return released[-1] if released else None

    def working(self) -> CanvasVersion:
        """The version a generator writes into: the latest while it is unpublished (no one has edited it yet), else a
        new one started from it."""
        latest = self.latest
        if latest is not None and latest.link is None:
            return latest
        return self.start_next()

    def unpublished(self) -> CanvasVersion:
        """The latest version, for a generator that only adds to the version being prepared; a published version is
        people's canvas, so this refuses it."""
        latest = self.latest
        if latest is None or latest.link is not None:
            raise PublishedVersion(f"{latest.folder.name if latest else 'no version'} is published; start the next version before generating into it")
        return latest
