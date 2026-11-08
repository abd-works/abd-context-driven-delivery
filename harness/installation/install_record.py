"""InstallRecord - the file that remembers what the last install wrote, so the next one can remove it."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from harness.installation.ide_layout import IdeLayout
from harness.installation.install_diagnostics import InstallDiagnostics

# The folders a skill, rule, command, prompt, or agent file sits under; cleaning stops emptying parents at them.
_CHANNEL_FOLDERS = ("skills", "rules", "commands", "prompts", "agents")
# Files an install updates in place and keeps across a clean: the MCP config and the diagnostics history.
_KEPT_FILES = frozenset({IdeLayout.MCP_CONFIG_NAME, InstallDiagnostics.NAME})


class InstallRecordUnreadable(Exception):
    """The install record is not the JSON it should be. Without it a clean cannot tell which files the last install
    wrote, so the install stops rather than overwrite the record and leave those files behind."""

    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(
            f"{path} is not a readable install record ({cause}); remove the files it lists by hand, or delete it and "
            "install again"
        )
        self.path = path
        self.cause = cause


class InstallRecord:
    """``.install-state.json``: the IDE and folder of the last install and every file it wrote, relative to that
    folder. An install adds each file it writes; a clean removes them and the folders they leave empty."""

    NAME = ".install-state.json"

    def __init__(self, path: Path) -> None:
        self.path = path
        self.installed_files: list[str] = []

    @property
    def saved(self) -> dict[str, Any]:
        """What the file holds; empty before the first install."""
        if not self.path.is_file():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise InstallRecordUnreadable(self.path, error) from error
        if not isinstance(data, dict):
            raise InstallRecordUnreadable(self.path, TypeError(f"expected an object, found {type(data).__name__}"))
        return data

    def track(self, written: Path, folder: Path) -> None:
        """Add written, a file the install wrote under folder."""
        try:
            relative = written.resolve().relative_to(folder.resolve()).as_posix()
        except ValueError:
            return
        if relative not in self.installed_files:
            self.installed_files.append(relative)

    def forget(self, relative: str) -> None:
        if relative in self.installed_files:
            self.installed_files.remove(relative)

    def keep_existing(self, folder: Path) -> None:
        """Start from the files the saved record lists that are still in folder, for an install that adds to it."""
        self.installed_files = [relative for relative in self.saved.get("installed_files", []) if (folder / relative).is_file()]

    def save(self, ide: str, folder: Path) -> None:
        payload = {"ide": ide, "path": str(folder), "installed_files": self.installed_files}
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def remove_installed(self, folder: Path) -> list[str]:
        """Remove every file the saved record lists for folder, and the folders that leaves empty; answer what was
        removed. A record of another folder removes nothing."""
        saved = self.saved
        if Path(str(saved.get("path", folder))).resolve() != folder.resolve():
            return []
        removed: list[str] = []
        for relative in saved.get("installed_files", []):
            target = folder / relative
            if Path(relative).name in _KEPT_FILES or not target.is_file():
                continue
            target.unlink()
            removed.append(relative)
            self.prune_empty_parents(target, folder)
        self.installed_files = []
        return removed

    def prune_empty_parents(self, removed: Path, folder: Path) -> None:
        """Remove the folders above removed that it left empty, up to its channel folder."""
        stop_at = {folder / name for name in _CHANNEL_FOLDERS}
        parent = removed.parent
        while parent not in stop_at and parent != folder:
            if not parent.is_dir() or any(parent.iterdir()):
                return
            try:
                parent.rmdir()
            except OSError:
                return
            parent = parent.parent

    def prune_empty_skill_folders(self, folder: Path) -> None:
        skills = folder / "skills"
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
