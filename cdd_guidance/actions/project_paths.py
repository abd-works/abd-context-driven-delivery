"""Paths a call names, read from the project of the session the call works in."""

from __future__ import annotations

from pathlib import Path


class PathsFromProject:
    """Mixed into a toolset made for a session (``self.session``): each path its call names is read the way the
    session's agent writes it, from the project's root or absolute.

    The cdd server serves every project from its own working folder, so a relative path read as given names a file in
    the server's checkout, not the project the call works on: the call answers nothing for a folder that is there, or
    reads and writes another checkout's files. The session already says which project it works in, so it decides.
    """

    def _from_project(self, named: str | Path) -> Path:
        """named as a path in this toolset's session's project; an absolute path stays where it is."""
        path = Path(named)
        if path.is_absolute():
            return path.resolve()
        return (self.session.repo_from_session() / path).resolve()
