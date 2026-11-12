"""A project for a spec to work in, so actions it runs write to their own session log instead of the one being worked on,
and what its chats open is kept in a cdd home of the spec run's own instead of the person's ``~/.cdd``."""

from __future__ import annotations

import atexit
import os
import shutil
import tempfile
from pathlib import Path

from harness.mcp.cdd_home import CDD_HOME_ENV


class SpecRunHome:
    """The cdd home of one spec run, named by ``CDD_HOME`` from the first spec that needs it until the run ends.

    Opening a session records it for its chat in ``open-sessions.json`` under the cdd home. A spec run with no
    ``CDD_HOME`` of its own would add every project it makes to the person's ``~/.cdd``, and the live server reads and
    rewrites that whole file on every session switch, so the file grew to thousands of spec projects and switches
    slowed. A run that names its own ``CDD_HOME``, as ``scripts/test.ps1`` does, keeps it."""

    _folder: Path | None = None

    @classmethod
    def ensure(cls) -> None:
        """Name a throwaway cdd home for this run, removed when the run ends, unless a cdd home is named already. Asked
        again by every spec, since a spec that names a home of its own for a while puts back no home when it is done."""
        if os.environ.get(CDD_HOME_ENV):
            return
        if cls._folder is None:
            cls._folder = Path(tempfile.mkdtemp(prefix="cdd-spec-home-"))
            atexit.register(shutil.rmtree, cls._folder, True)
        os.environ[CDD_HOME_ENV] = str(cls._folder)


class ThrowawayProject:
    """An empty project named by ``CDD_PROJECT`` while a spec runs. An action writes a line to the open session's log,
    and run in this repository the open session is whoever is working here, so a spec's actions land in that person's
    log and the session board counts them as their work. What its chats open goes in the spec run's own cdd home.
    ``close_all`` closes every project still open, from an ``after.each``. A project given a name gets a folder of that
    name, for a spec that reads the project's name."""

    _open: list[ThrowawayProject] = []

    def __init__(self, name: str = "") -> None:
        SpecRunHome.ensure()
        self._folder = Path(tempfile.mkdtemp(prefix="cdd-spec-project-"))
        self.root = (self._folder / name).resolve() if name else self._folder
        self.root.mkdir(exist_ok=True)
        self._saved = os.environ.get("CDD_PROJECT")
        os.environ["CDD_PROJECT"] = str(self.root)
        type(self)._open.append(self)

    @property
    def folder(self) -> Path:
        """The temporary folder the project sits in, which holds what a spec keeps beside the project, such as its git
        origin; the project itself when it has no name."""
        return self._folder

    @classmethod
    def close_all(cls) -> None:
        while cls._open:
            cls._open[-1].close()

    def close(self) -> None:
        """Name the project that was named before, and remove this one."""
        if self in type(self)._open:
            type(self)._open.remove(self)
        if self._saved is None:
            os.environ.pop("CDD_PROJECT", None)
        else:
            os.environ["CDD_PROJECT"] = self._saved
        shutil.rmtree(self._folder, ignore_errors=True)
