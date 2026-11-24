"""FolderDeletion - deleting a folder a checkout left behind, whatever Windows says about its files."""

from __future__ import annotations

import logging
import os
import shutil
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class FolderDeletion:
    """The deletion of one folder a checkout or git left behind: a removed worktree's folder, a leftover folder beside the
    main clone, or git's record of a worktree whose folder is gone. Windows refuses to delete a read-only file, a file
    another account owns, and a path past 260 characters, so each is cleared before the folder is given up on: read-only
    flags are cleared, the folder is taken over by the person's account and granted to it, and the path is given the
    long-path prefix. A folder a running program works in still cannot be deleted; ``delete`` then answers false."""

    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def delete(self) -> bool:
        """Delete the folder and everything in it, taking it over on Windows when a plain delete leaves it there. Answer
        whether it is gone."""
        self._remove_tree()
        if self._folder.exists() and os.name == "nt":
            self._take_over()
            self._remove_tree()
        if self._folder.exists() and os.name == "nt":
            self._remove_with_powershell()
        return not self._folder.exists()

    def _remove_tree(self) -> None:
        if self._folder.exists():
            shutil.rmtree(self._long_path(), onexc=self._made_writable_and_retried)

    def _made_writable_and_retried(self, function: Callable[[str], object], path: str, error: BaseException) -> None:
        """A read-only file refuses deletion on Windows until its flag is cleared; a file a running program holds stays,
        and the folder's deletion is answered by whether the folder is still there."""
        try:
            os.chmod(path, stat.S_IWRITE)
            function(path)
        except OSError as again:
            logger.info("could not delete %s: %s (first %s)", path, again, error)

    def _take_over(self) -> None:
        """What was done by hand on 2026-11-24 to git's records that refused deletion: clear every read-only flag, take
        ownership of the folder and everything in it, and grant the person's account full control, inherited."""
        user = os.environ.get("USERNAME", "").strip()
        target = str(self._folder)
        commands = [("attrib", "-R", f"{target}\\*", "/S", "/D")]
        if user:
            commands += [("takeown", "/F", target, "/R", "/D", "Y"), ("icacls", target, "/grant", f"{user}:(OI)(CI)F", "/T", "/C")]
        for command in commands:
            self._run(command)

    def _remove_with_powershell(self) -> None:
        self._run(("powershell", "-NoProfile", "-NonInteractive", "-Command", f'Remove-Item -LiteralPath "{self._folder}" -Recurse -Force -ErrorAction SilentlyContinue'))

    def _run(self, command: tuple[str, ...]) -> None:
        try:
            subprocess.run(list(command), capture_output=True, check=False)
        except OSError as exc:
            logger.info("%s failed for %s: %s", command[0], self._folder, exc)

    def _long_path(self) -> str:
        """Windows refuses paths past 260 characters unless they carry the \\\\?\\ prefix, and a checkout's retired
        fixtures run past it, so their files would outlive the folder."""
        resolved = str(self._folder.resolve())
        if os.name != "nt" or resolved.startswith("\\\\?\\"):
            return resolved
        return "\\\\?\\" + resolved
