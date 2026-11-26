"""SessionPaths - how one session names the paths a call gives it: from its project's top, under its root, or in its
``.context`` folder."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.guidance.documents import load_document

if TYPE_CHECKING:
    from space.session.session import Session


class SessionPaths:
    """The paths of one session's project as its calls and its board name them. The cdd server serves every project
    from its own working folder, so a relative path read as given would name a file in the server's checkout; every
    path a call names is read here, from the session's project."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # Each path text this session has resolved, with the folder it resolved to.
        self._resolved_paths: dict[str, Path] = {}

    def resolved(self, path: Path) -> Path:
        """path resolved, once for each path text: a board read asks the same few folders thousands of times, and on
        Windows each resolve asks the disk."""
        named = str(path)
        held = self._resolved_paths.get(named)
        if held is None:
            held = self._resolved_paths[named] = path.resolve()
        return held

    def folder_under_root(self, relative: str) -> Path:
        """The folder relative names under the session's root, such as a practice's chosen root, resolved."""
        return self.resolved(self._session.work_root / relative)

    def context_folder(self, module: str = "") -> Path:
        """The .context folder of the session's root, or of a module folder under it, where sketches and grill answers
        go so they outlast the session. A module named as a .context folder is that folder, and a root inside a .context
        or .sessions folder uses that project's .context, so nothing is written into a session's own folder."""
        root = self._session.work_root
        folder = root / module if module else root
        for candidate in (folder, *folder.parents):
            if candidate.name == ".context":
                return candidate
            if candidate.name == ".sessions":
                return candidate.parent / ".context"
        return folder / ".context"

    def sketch(self, module: str = "") -> Path:
        """The session's sketch, in the .context folder of its root or of a module under it: a session is named for the
        subject it works on, so its sketch is too, and one file holds every practice's section."""
        return self.context_folder(module) / self._sketch_name

    def is_sketch(self, file: Path) -> bool:
        """Whether file is the session's sketch, of its root or of a module under it."""
        return file.name == self._sketch_name and file.parent.name == ".context"

    @property
    def _sketch_name(self) -> str:
        return f"{self._session.name or 'main'}-sketch.md"

    def path_named(self, named: str | Path) -> Path:
        """named as a path in this session's project, the way its agent writes one: from the project's root, or
        absolute."""
        path = Path(named)
        return path.resolve() if path.is_absolute() else (self._session.checkout.root / path).resolve()

    def document_named(self, content: str = "", paths: list[str] | str | None = None) -> str:
        """The document a call names: content, or the files at paths, read from this session's project."""
        if paths in ("", None, []):
            return load_document(content)
        entries = [paths] if isinstance(paths, (str, Path)) else list(paths)
        return load_document(content, [str(self.path_named(entry)) for entry in entries])

    def from_project(self, path: Path | str) -> str:
        """path as written from the project's top, the way the board names every file and folder."""
        return self._session.repo.path_from_top(path)

    def in_project(self, paths: list[str]) -> list[str]:
        """paths, named from the project, as the graph view's graph names its files, which it reads from the project's
        top; any outside the project left out."""
        project = self._session.checkout.root.resolve()
        return [found.relative_to(project).as_posix() for found in map(self.path_named, paths) if found.is_relative_to(project)]
