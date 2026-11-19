"""InstallRecord - the file an IDE folder keeps of what the install into it wrote, so the next install or a clean can
remove it; and LastInstall, the folder a checkout last installed into."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import InstallDiagnostics
from harness.installation.install_target import InstallTarget
from harness.installation.json_file import JsonFile, JsonFileUnreadable

# The folders a skill, rule, command, prompt, or agent file sits under; cleaning stops emptying parents at them.
_CHANNEL_FOLDERS = ("skills", "rules", "commands", "prompts", "agents")
# Files an install updates in place and keeps across a clean: the MCP config and the diagnostics history.
_KEPT_FILES = frozenset({IdeLayout.MCP_CONFIG_NAME, InstallDiagnostics.NAME})
_INSTALLED_FILES = "installed_files"


class InstallRecordUnreadable(JsonFileUnreadable):
    """The install record is not the JSON it should be. Without it a clean cannot tell which files the last install
    wrote, so the install stops rather than overwrite the record and leave those files behind."""

    def message(self, path: Path, cause: Exception) -> str:
        return (
            f"{path} is not a readable install record ({cause}); remove the files it lists by hand, or delete it and "
            "install again"
        )


class InstallRecord:
    """``.install-state.json`` in the IDE folder an install writes into: the IDE, the folder's whole path, and every
    file the install wrote, relative to the folder. Each folder keeps its own, so an install into another folder leaves
    this one's files known. It is saved as each file is written, so an install stopped halfway still lists what it
    wrote; a clean removes those files and the folders they leave empty."""

    NAME = ".install-state.json"

    def __init__(self, target: InstallTarget) -> None:
        self.folder = target.path
        self.ide = target.layout.ide
        self.path = self.folder / self.NAME
        self._file = JsonFile(self.path, InstallRecordUnreadable)
        self.installed_files: list[str] = []

    @property
    def saved(self) -> dict[str, Any]:
        """What the file holds; empty before the first install into the folder."""
        return self._file.read()

    def track(self, written: Path) -> None:
        """Add written, a file the install wrote under the folder, and save, so the file is known from now on."""
        try:
            relative = written.resolve().relative_to(self.folder.resolve()).as_posix()
        except ValueError:
            return
        if relative not in self.installed_files:
            self.installed_files.append(relative)
            self.save()

    def forget(self, relative: str) -> None:
        """Drop relative, a file the install removed again, and save."""
        if relative in self.installed_files:
            self.installed_files.remove(relative)
            self.save()

    def keep_existing(self) -> None:
        """Start from the files the saved record lists that are still in the folder, for an install that adds to it."""
        self.installed_files = [relative for relative in self.saved.get(_INSTALLED_FILES, []) if (self.folder / relative).is_file()]

    def adopt(self, installed_files: list[str]) -> None:
        """Take installed_files as what the last install into the folder wrote, and save: the list an earlier CDD kept
        for this folder outside it."""
        self.installed_files = list(installed_files)
        self.save()

    def save(self) -> None:
        self._file.write({"ide": self.ide, "path": str(self.folder), _INSTALLED_FILES: self.installed_files})

    def remove_installed(self) -> list[str]:
        """Remove every file the saved record lists, and the folders that leaves empty; answer what was removed. A
        folder nothing was installed into has no record, and nothing is removed or written."""
        saved = self.saved
        removed: list[str] = []
        for relative in saved.get(_INSTALLED_FILES, []):
            target = self.folder / relative
            if Path(relative).name in _KEPT_FILES or not target.is_file():
                continue
            target.unlink()
            removed.append(relative)
            self.prune_empty_parents(target)
        self.installed_files = []
        if saved:
            self.save()
        return removed

    def prune_empty_parents(self, removed: Path) -> None:
        """Remove the folders above removed that it left empty, up to its channel folder."""
        stop_at = {self.folder / name for name in _CHANNEL_FOLDERS}
        parent = removed.parent
        while parent not in stop_at and parent != self.folder:
            if not parent.is_dir() or any(parent.iterdir()):
                return
            try:
                parent.rmdir()
            except OSError:
                return
            parent = parent.parent

    def prune_empty_skill_folders(self) -> None:
        skills = self.folder / "skills"
        if not skills.is_dir():
            return
        for dirpath, _dirnames, _filenames in os.walk(skills, topdown=False):
            candidate = Path(dirpath)
            if candidate != skills and not any(candidate.iterdir()):
                self._remove_empty_folder(candidate)

    def _remove_empty_folder(self, folder: Path) -> None:
        """A running Claude Code watches its skills folders, so Windows refuses to remove one it holds open; the empty
        folder stays until the next install."""
        try:
            folder.rmdir()
        except PermissionError:
            return


class LastInstall:
    """The IDE and folder a checkout last installed into, kept in one file beside the installer: an install or a clean
    that names neither goes there. It lists no files; each folder's *InstallRecord* does. An install into a temporary
    folder is not remembered, so a spec's install never replaces the person's."""

    def __init__(self, path: Path) -> None:
        self._file = JsonFile(path, InstallRecordUnreadable)

    @property
    def saved(self) -> dict[str, Any]:
        """The ``ide`` and ``path`` of the last install; empty before the first."""
        return self._file.read()

    def remember(self, target: InstallTarget) -> None:
        """Keep target as the folder last installed into, unless it is a temporary one."""
        if not target.is_temporary:
            self._file.write({"ide": target.layout.ide, "path": str(target.path)})

    def hand_over_to(self, record: InstallRecord) -> None:
        """Give record the files this file lists for its folder, while that folder keeps no record of its own. A CDD
        before each folder kept its own record listed the last install's files here; without them the first clean by
        this CDD would leave that install's renamed or deleted files in the folder for good."""
        saved = self.saved
        if _INSTALLED_FILES not in saved or record.path.exists() or not record.folder.is_dir():
            return
        if Path(str(saved.get("path", ""))).resolve() == record.folder.resolve():
            record.adopt(saved[_INSTALLED_FILES])
