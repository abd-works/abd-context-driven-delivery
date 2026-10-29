"""Repo ``.sessions/session.json`` — the branch, worktree, and session in use."""
from __future__ import annotations

import json
import os
from pathlib import Path

STATE_NAME = "session.json"
DESIGN_CANVAS_FOLDER = "design-canvas"
E2E_RESULTS_FOLDER = "e2e-test-results"
_LEGACY_SESSION_KEY = "current"


class WorkState:
    """The open branch, worktree, and session, shared by the repo and session commands."""

    def __init__(self, repo_root: Path | str) -> None:
        self.root = Path(repo_root).resolve()

    @property
    def path(self) -> Path:
        return self.root / ".sessions" / STATE_NAME

    @property
    def branch(self) -> str:
        return self._value("branch")

    @branch.setter
    def branch(self, name: str) -> None:
        self._store("branch", name)

    @property
    def worktree(self) -> str:
        return self._value("worktree")

    @worktree.setter
    def worktree(self, path: str) -> None:
        self._store("worktree", path)

    @property
    def session(self) -> str:
        return self._value("session")

    @session.setter
    def session(self, name: str) -> None:
        self._store("session", name)

    @property
    def release(self) -> str:
        """The release this checkout's work belongs to: the open session, else the branch, else ``default``."""
        return self.session or self.branch or "default"

    def release_folder(self, release: str = "") -> Path:
        """``.sessions/<release>/``: the release's session files, its design canvas, and its end-to-end results."""
        return self.root / ".sessions" / (release or self.release)

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
        # WHY: every MCP host saves the session when it starts, and sessions start together.
        # An unchanged value is not written, and a changed one is swapped in whole, so hosts
        # starting at once neither collide on the file nor read it half written.
        data = self.load()
        cleaned = str(value or "").strip()
        if data.get(key, "") == cleaned:
            return
        if cleaned:
            data[key] = cleaned
        else:
            data.pop(key, None)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        staged = self.path.with_name(f"{self.path.name}.{os.getpid()}.tmp")
        staged.write_text(json.dumps(data), encoding="utf-8")
        os.replace(staged, self.path)
