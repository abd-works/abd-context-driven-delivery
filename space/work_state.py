"""Repo ``.sessions/session.json`` — the branch, worktree, and session in use."""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

SESSIONS_FOLDER = ".sessions"
STATE_NAME = "session.json"
E2E_RESULTS_FOLDER = "e2e-test-results"
_LEGACY_SESSION_KEY = "current"


class WorkState:
    """The open branch, worktree, and session of one checkout, saved by name in its ``.sessions/session.json`` and
    shared by the repo and session commands. It keeps names only: the repository turns a branch name into its *Branch*
    and a worktree's folder into its *Worktree*."""

    def __init__(self, repo_root: Path | str) -> None:
        self.root = Path(repo_root).resolve()

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

    @property
    def release(self) -> str:
        """The release this checkout's work belongs to: the open session, else the branch, else ``main``."""
        return self.session or self._value("branch") or "main"

    def release_folder(self, release: str = "") -> Path:
        """``.sessions/<release>/``: the release's session files, its design canvas, and its end-to-end results."""
        return self.sessions_folder / (release or self.release)

    def load(self) -> dict[str, str]:
        if not self.path.is_file():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        # Files written before the branch and worktree keys named the session "current".
        legacy = data.pop(_LEGACY_SESSION_KEY, None)
        if legacy and not data.get("session"):
            data["session"] = legacy
        return {str(key): str(value) for key, value in data.items() if str(value).strip()}

    def _value(self, key: str) -> str:
        return self.load().get(key, "").strip()

    def _store(self, key: str, value: str) -> None:
        # WHY: calls from several chats save the session at once. An unchanged value is not written, and a
        # changed one is swapped in whole from a file of its own thread, so writers neither collide on the file
        # nor read it half written.
        data = self.load()
        cleaned = str(value or "").strip()
        if data.get(key, "") == cleaned:
            return
        if cleaned:
            data[key] = cleaned
        else:
            data.pop(key, None)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        staged = self.path.with_name(f"{self.path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        staged.write_text(json.dumps(data), encoding="utf-8")
        os.replace(staged, self.path)
