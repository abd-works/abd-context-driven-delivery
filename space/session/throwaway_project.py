"""A project for a spec to work in, so actions it runs write to their own session log instead of the one being worked on."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from space.session.session import Session
from space.work_state import working_on


class ThrowawayProject:
    """An empty project named by ``CDD_PROJECT`` while a spec runs. An action writes a line to the open session's log,
    and run in this repository the open session is whoever is working here, so a spec's actions land in that person's
    log and the session board counts them as their work. ``close_all`` closes every project still open, from an
    ``after.each``."""

    _open: list[ThrowawayProject] = []

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-spec-project-"))
        self._saved = os.environ.get("CDD_PROJECT")
        os.environ["CDD_PROJECT"] = str(self.root)
        Session.forget_current()
        type(self)._open.append(self)

    @classmethod
    def close_all(cls) -> None:
        while cls._open:
            cls._open[-1].close()

    def close(self) -> None:
        """Name the project that was named before, and remove this one."""
        if self in type(self)._open:
            type(self)._open.remove(self)
        Session.forget_current()
        if self._saved is None:
            os.environ.pop("CDD_PROJECT", None)
        else:
            os.environ["CDD_PROJECT"] = self._saved
        shutil.rmtree(self.root, ignore_errors=True)


class ProjectCall:
    """A spec's calls on one project, made the way the cdd server makes a chat's calls: inside, the project being worked
    on, and so the current session, is that project's. ``close_all`` ends every call still open, from an ``after.each``."""

    _open: list[ProjectCall] = []

    def __init__(self, project: Path | str) -> None:
        self._call = working_on(project)
        self._call.__enter__()
        type(self)._open.append(self)

    @classmethod
    def close_all(cls) -> None:
        while cls._open:
            cls._open.pop()._call.__exit__(None, None, None)
