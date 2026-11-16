"""InstallTarget - the IDE folder one install writes into, with that IDE's layout."""
from __future__ import annotations

import functools
from pathlib import Path

from harness.installation.destination import is_temporary
from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import InstallDiagnostics


class InstallTarget:
    """The IDE folder one install writes into, with that IDE's layout: where every channel of the install writes its
    files, and the ``diagnostics.json`` the install keeps there (``diagnostics``), made once."""

    def __init__(self, layout: IdeLayout, path: Path | str) -> None:
        self.layout = layout
        self.path = Path(path)

    @classmethod
    def from_last_install(cls, layout: IdeLayout, last: str | None, repo: Path) -> InstallTarget:
        """The folder the last install wrote into, last, while it is there and not a temporary one; else repo's own
        folder for layout's IDE."""
        if last and Path(last).exists() and not is_temporary(Path(last)):
            return cls(layout, last)
        return cls(layout, repo / layout.folder_name)

    @property
    def is_temporary(self) -> bool:
        """Whether the folder is in the system's temporary folder, as a spec's install is."""
        return is_temporary(self.path)

    @functools.cached_property
    def diagnostics(self) -> InstallDiagnostics:
        """The install's ``diagnostics.json`` in this folder, made once."""
        return InstallDiagnostics(self.path, self.layout)
