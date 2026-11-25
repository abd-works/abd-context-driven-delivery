"""Numbered versions of a design canvas: ``version-1``, ``version-2``, … beside each other under one folder, the
``design-canvas`` folder in the UX practice's root.

People edit a published canvas directly, so a regeneration never writes over one: it starts the next version, a
copy of the latest that the generator then renders into, and that version is published as a new canvas.
``versions.json`` remembers each version's published link, in the order they were published (*PublishedLinks*). A
version is recorded as published only after a walk of its screens (*WalkedScreens*, the UX practice's story canvas
walk) finds every value its scenarios' steps name on the screen that shows the step, and a change on the screen after each
action, or the person accepts by name each value left out and each action that leaves its screen as it was; the
accepted ones are kept beside the link, so the gap stays in view. A
version kept as a release is renamed to the release's name (``CanvasVersion.release``); numbering then starts again at
``version-1``, copied from that release.

A project that wants one canvas regenerated in place, until it wants versions again, sets ``"keep_one": true`` in
``versions.json``: the render then writes into the latest version even once it is published, and publishing records the
same link again. The walk before publishing still runs.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import List, Optional, Protocol, Sequence

from harness.installation.json_file import JsonFile
from harness.installation.published_links import PublishedLinks

# The folder a canvas is kept in, under the UX practice's root, where the UX practice writes its other outputs.
DESIGN_CANVAS_FOLDER = "design-canvas"
_VERSION = re.compile(r"^version-(\d+)$")
# What a published version keeps beside its link: the values its screens leave out that the person accepted.
_ACCEPTED_MISSES = "accepted_misses"
# The setting in versions.json that keeps one canvas every render updates in place, instead of a new version each time.
KEEP_ONE = "keep_one"
# The name of the canvas of the whole repository, the UX practice's mockup; a canvas scoped to an increment, a feature,
# an epic or a module puts the scope's name in front, as other formats name their scoped files (``{scope}-ux-mockup``).
CANVAS_NAME = "ux-mockup"


def canvas_name(scope: str = "") -> str:
    """The canvas's name: ``ux-mockup`` for the whole repository, ``{scope}-ux-mockup`` for one scoped to scope."""
    return f"{scope}-{CANVAS_NAME}" if scope else CANVAS_NAME


class PublishedVersion(Exception):
    """A generator tried to write into a version that is already published, where people may have edited it."""


class WalkedScreens(Protocol):
    """A walk of a version's screens, each rendered at its scenarios' steps: what it found missing. Each miss names a
    value a step names and its screen leaves out, as ``Story › Scenario › value``."""

    @property
    def misses(self) -> Sequence[str]: ...


class UnshownStepValues(Exception):
    """A version was about to be recorded as published while its screens leave out values their scenarios' steps name,
    and the person has not accepted those gaps by name."""

    def __init__(self, version: str, misses: Sequence[str]) -> None:
        listed = "\n".join(f"  - {miss}" for miss in misses)
        super().__init__(
            f"{version} is not recorded as published: its screens leave out {len(misses)} value(s) their steps name, or stay "
            f"as they were after an action. Make each screen show them and each action change its screen, or pass the ones "
            f"the prototype cannot show as accepted_misses:\n{listed}")
        self.version = version
        self.misses = list(misses)


class CanvasVersion:
    """One version of a canvas: its folder, which holds ``project/`` exactly as the canvas publishes it, its number
    (none for a version kept as a release), the link it was published at, and the canvas's name, which its title
    starts with."""

    def __init__(self, folder: Path, published: PublishedLinks, name: str) -> None:
        self.folder = folder
        self._published = published
        self._name = name

    @property
    def number(self) -> Optional[int]:
        """The version's number; none for a version kept as a release under its release's name."""
        found = _VERSION.match(self.folder.name)
        return int(found.group(1)) if found else None

    @property
    def link(self) -> Optional[str]:
        """The link the version was published at; none while it is unpublished."""
        return self._published.of(self.folder.name)

    @property
    def title(self) -> str:
        """The title the version is published under: the canvas's name, then the version's folder, as a versioned file
        is named (``ux-mockup.version-7``), so a person can tell canvases apart and match each to its folder."""
        return f"{self._name}.{self.folder.name}"

    @property
    def accepted_misses(self) -> List[str]:
        """The values its screens leave out that the person accepted when it was published."""
        return list(self._published.beside(self.folder.name).get(_ACCEPTED_MISSES, []))

    def publish_at(self, url: str, walk: WalkedScreens, accepted_misses: Sequence[str] = ()) -> None:
        """Keep url as the link the version was published at, once walk finds every value the steps name on its
        screens. A value left out is refused (*UnshownStepValues*) unless accepted_misses names it, because a screen
        that ignores its scenario shows the reader a story the scenario does not tell; the accepted ones are kept
        beside the link."""
        accepted = set(accepted_misses)
        unaccepted = [miss for miss in walk.misses if miss not in accepted]
        if unaccepted:
            raise UnshownStepValues(self.folder.name, unaccepted)
        kept = [miss for miss in walk.misses if miss in accepted]
        self._published.record(self.folder.name, url, {_ACCEPTED_MISSES: kept} if kept else None)

    def release(self, name: str) -> CanvasVersion:
        """Keep this published version as the release name: its folder and its link take the release's name."""
        target = self.folder.parent / name
        self.folder.rename(target)
        self._published.rename(self.folder.name, name)
        return CanvasVersion(target, self._published, self._name)


class CanvasVersions:
    """The versions of the canvas kept under root (for example ``<ux root>/design-canvas``), named for scope: the whole
    repository when scope is empty (``ux-mockup``), else the increment, feature, epic or module it names
    (``{scope}-ux-mockup``)."""

    def __init__(self, root: str | Path, scope: str = "") -> None:
        self.root = Path(root)
        self.name = canvas_name(scope)
        self._record = JsonFile(self.root / "versions.json")
        self.published = PublishedLinks(self._record)

    @property
    def keeps_one(self) -> bool:
        """Whether the project keeps one canvas that every render updates in place, set by ``"keep_one": true`` in
        ``versions.json``; off unless set, so a published version is never written over by accident."""
        return self._record.read().get(KEEP_ONE) is True

    @classmethod
    def in_practice_root(cls, practice_root: str | Path, scope: str = "") -> CanvasVersions:
        """The canvas the UX practice keeps in its root, the folder session.json names for it (``practices.ux.root``),
        beside its other outputs, named for scope."""
        return cls(Path(practice_root) / DESIGN_CANVAS_FOLDER, scope)

    @property
    def _numbers(self) -> List[int]:
        if not self.root.is_dir():
            return []
        found = (_VERSION.match(path.name) for path in self.root.iterdir() if path.is_dir())
        return sorted(int(match.group(1)) for match in found if match)

    def _numbered(self, number: int) -> CanvasVersion:
        return CanvasVersion(self.root / f"version-{number}", self.published, self.name)

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
        new one started from it. A canvas that keeps one version (*keeps_one*) answers the latest even once it is
        published, so the render updates that canvas in place and it is published again at the same link."""
        latest = self.latest
        if latest is not None and (latest.link is None or self.keeps_one):
            return latest
        return self.start_next()

    def unpublished(self) -> CanvasVersion:
        """The latest version, for a generator that only adds to the version being prepared; a published version is
        people's canvas, so this refuses it, unless the canvas keeps one version (*keeps_one*) that every render
        updates in place."""
        latest = self.latest
        if latest is None or (latest.link is not None and not self.keeps_one):
            raise PublishedVersion(f"{latest.folder.name if latest else 'no version'} is published; start the next version before generating into it")
        return latest
