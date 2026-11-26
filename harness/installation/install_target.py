"""InstallTarget - the IDE folder one install writes into, with that IDE's layout."""
from __future__ import annotations

import functools
import os
import tempfile
from pathlib import Path

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import InstallDiagnostics


def is_temporary(folder: Path) -> bool:
    """Whether folder is in the system's temporary folder, as a spec's install is: such an install keeps its record and
    its MCP entry in the folder itself, so it never touches the person's own."""
    try:
        temp = _resolved_temp()
        resolved = Path(folder).resolve()
    except OSError:
        return False
    return resolved == temp or temp in resolved.parents


@functools.cache
def _resolved_temp() -> Path:
    """The system's temporary folder, resolved once: it does not move while a process runs, and resolving a path on
    Windows asks the file system for every folder in it."""
    return Path(tempfile.gettempdir()).resolve()


class NotAnInstallFolder(ValueError):
    """An install was told to write into something that cannot be an IDE folder: an empty path, which would be whatever
    directory the command runs in, a file, or a folder whose parent does not exist. Nothing is written."""

    def __init__(self, path: Path | str, reason: str) -> None:
        super().__init__(f"{str(path)!r} {reason}")
        self.path = path


class InstallTarget:
    """The IDE folder one install writes into, with that IDE's layout: where every channel of the install writes its
    files, and the ``diagnostics.json`` the install keeps there (``diagnostics``), made once. ``dev_lane`` is whether
    the install was asked to point the chats of the project it installs into at the dev lane's cdd server; a project
    other than the checkout installing it is otherwise pointed at the stable lane, whichever lane that checkout runs on."""

    def __init__(self, layout: IdeLayout, path: Path | str, dev_lane: bool = False) -> None:
        if not str(path).strip():
            raise NotAnInstallFolder(path, "is empty: name the IDE folder to install into, such as .claude")
        if Path(path).is_file():
            raise NotAnInstallFolder(path, "is a file, and an install writes into a folder")
        # The whole path, so the record an install saves is found by a clean run from any other directory.
        whole = Path(os.path.abspath(path))
        # An install makes the IDE folder itself, never the folders above it, so a mistyped path makes no new tree.
        if not whole.parent.is_dir():
            raise NotAnInstallFolder(path, f"is in {whole.parent}, which does not exist: an install makes only the IDE folder itself")
        self.layout = layout
        self.path = whole
        self.dev_lane = dev_lane

    @classmethod
    def from_last_install(cls, layout: IdeLayout, last: str | None, repo: Path, dev_lane: bool = False) -> InstallTarget:
        """The folder the last install wrote into, last, while it is there and not a temporary one; else repo's own
        folder for layout's IDE."""
        if last and Path(last).exists() and not is_temporary(Path(last)):
            return cls(layout, last, dev_lane)
        return cls(layout, repo / layout.folder_name, dev_lane)

    @property
    def is_temporary(self) -> bool:
        """Whether the folder is in the system's temporary folder, as a spec's install is."""
        return is_temporary(self.path)

    @functools.cached_property
    def diagnostics(self) -> InstallDiagnostics:
        """The install's ``diagnostics.json`` in this folder, made once."""
        return InstallDiagnostics(self.path)
