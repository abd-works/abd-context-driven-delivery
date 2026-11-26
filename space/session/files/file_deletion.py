"""FileDeletion - the delete of one file or folder a person chose in the Files app's file menu, checked whole before
anything is deleted."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterator

from space.session.files.file_manager import OwnRecord, SessionRecordWriteRefused, VersionControlPathRefused, inside_version_control, is_link
from space.session.session_record import SESSION_FILE


class ReadOnlyDeleteRefused(PermissionError):
    """A delete of a read-only file, or of a folder holding one: Windows refuses to delete it, so a folder's delete would
    stop half-way, with part of the folder gone. It names the path refused and the read-only file."""

    def __init__(self, path: str, read_only: str) -> None:
        held = f" holds {read_only}, which" if read_only else ""
        super().__init__(f"{path}{held} is read-only, so nothing was deleted: make it writable first if it is to go")
        self.path = path


class FolderPartlyDeleted(OSError):
    """A folder's delete that the file system stopped part of the way, after every check passed, such as on a file
    another program holds open: part of the folder is gone and the rest is still there. It names the folder and the
    file system's reason, so nobody reads it as a delete that changed nothing."""

    def __init__(self, path: str, reason: OSError) -> None:
        super().__init__(f"{path} was only partly deleted: {reason}; what was not deleted is still there")
        self.path = path


class FileDeletion:
    """The delete of target, the file, folder or link path names: a link is removed and what it points to kept; a
    folder goes with every file in it, but only once every path it holds was checked, so a delete the session refuses
    deletes nothing. Refused: a folder holding a .git folder, the session's own session.json or a folder holding it,
    and a read-only file or a folder holding one."""

    def __init__(self, path: str, target: Path, record: OwnRecord) -> None:
        self._path = path
        self._target = target
        self._record = record

    def run(self) -> None:
        """Delete the target once nothing it removes is refused."""
        if is_link(self._target):
            self._target.unlink()
            return
        for removed in self._removed():
            self._refuse(removed)
        if not self._target.is_dir():
            self._target.unlink()
            return
        try:
            shutil.rmtree(self._target)
        except OSError as reason:
            raise FolderPartlyDeleted(self._path, reason) from reason

    def _removed(self) -> Iterator[Path]:
        """The target and every path under it, never through a link, since the delete removes a link, not what it points to."""
        yield self._target
        folders = [self._target] if self._target.is_dir() else []
        while folders:
            with os.scandir(folders.pop()) as entries:
                for entry in entries:
                    yield Path(entry.path)
                    if entry.is_dir(follow_symlinks=False) and not is_link(entry):
                        folders.append(Path(entry.path))

    def _refuse(self, removed: Path) -> None:
        """Raise the refusal of removed, a path the delete would remove, when it may not go."""
        held = "" if removed == self._target else removed.relative_to(self._target).as_posix()
        if inside_version_control((removed.name,)):
            raise VersionControlPathRefused(self._path, held)
        if removed.name.casefold() == SESSION_FILE and self._record.is_its_file(removed):
            raise SessionRecordWriteRefused(self._path)
        if not is_link(removed) and removed.is_file() and not os.access(removed, os.W_OK):
            raise ReadOnlyDeleteRefused(self._path, held)
