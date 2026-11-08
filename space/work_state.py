"""Repo ``.sessions/session.json`` — the branch, worktree, and session in use."""
from __future__ import annotations

from pathlib import Path

from harness.installation.json_file import JsonFile

SESSIONS_FOLDER = ".sessions"
STATE_NAME = "session.json"
E2E_RESULTS_FOLDER = "e2e-test-results"


class WorkState:
    """The open branch, worktree, and session of one checkout, saved by name in its ``.sessions/session.json`` and
    shared by the repo and session commands. It keeps names only: the repository turns a branch name into its *Branch*
    and a worktree's folder into its *Worktree*."""

    def __init__(self, repo_root: Path | str) -> None:
        self.root = Path(repo_root).resolve()
        self._file = JsonFile(self.path)

    @property
    def sessions_folder(self) -> Path:
        return self.root / SESSIONS_FOLDER

    @property
    def path(self) -> Path:
        return self.sessions_folder / STATE_NAME

    @property
    def branch_name(self) -> str:
        """The name of the branch saved as open on this checkout; empty when none is saved."""
        return self._value("branch")

    @branch_name.setter
    def branch_name(self, name: str) -> None:
        self._store("branch", name)

    @property
    def worktree_folder(self) -> Path | None:
        """The folder of the worktree saved as open; none when no worktree is open."""
        path = self._value("worktree")
        return Path(path) if path else None

    @worktree_folder.setter
    def worktree_folder(self, folder: Path | None) -> None:
        self._store("worktree", str(folder) if folder is not None else "")

    @property
    def session(self) -> str:
        return self._value("session")

    @session.setter
    def session(self, name: str) -> None:
        self._store("session", name)

    def load(self) -> dict[str, str]:
        return {str(key): str(value) for key, value in self._file.read().items() if str(value).strip()}

    def _value(self, key: str) -> str:
        return self.load().get(key, "").strip()

    def _store(self, key: str, value: str) -> None:
        # WHY: calls from several chats save the session at once. An unchanged value is not written, and a changed one
        # is swapped in whole (JsonFile.write), so writers neither collide on the file nor read it half written.
        data = self.load()
        cleaned = str(value or "").strip()
        if data.get(key, "") == cleaned:
            return
        if cleaned:
            data[key] = cleaned
        else:
            data.pop(key, None)
        self._file.write(data)
