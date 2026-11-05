"""Repo ``.sessions/session.json`` — the branch, worktree, and session in use."""
from __future__ import annotations

import json
import os
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path

SESSIONS_FOLDER = ".sessions"
STATE_NAME = "session.json"
DESIGN_CANVAS_FOLDER = "design-canvas"
E2E_RESULTS_FOLDER = "e2e-test-results"
_LEGACY_SESSION_KEY = "current"
# One cdd server answers every chat, so the project belongs to the call, not to the process.
_called_project: ContextVar[Path | None] = ContextVar("cdd_called_project", default=None)


def checkout_holding(path: Path | str) -> Path:
    """The git checkout containing ``path``; ``path`` itself when it is not inside one."""
    resolved = Path(path).resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / ".git").exists():
            return candidate
    return resolved


def main_checkout_of(checkout: Path | str) -> Path:
    """The repository's main checkout. A linked worktree's ``.git`` is a file naming its git folder, whose
    ``commondir`` leads back to the main checkout's ``.git``; any other checkout is its own main checkout."""
    root = Path(checkout).resolve()
    marker = root / ".git"
    if not marker.is_file():
        return root
    worktree_git = (root / marker.read_text(encoding="utf-8").split("gitdir:", 1)[-1].strip()).resolve()
    common = worktree_git / "commondir"
    if not common.is_file():
        return root
    return (worktree_git / common.read_text(encoding="utf-8").strip()).resolve().parent


def project_folder() -> Path:
    """The folder of the project being worked on: the one the running call names, else ``CDD_PROJECT``, else the
    current folder.

    ``CDD_REPO`` names the CDD checkout that serves the tools, not the project, so it never picks the project."""
    called = _called_project.get()
    if called is not None:
        return called
    named = os.environ.get("CDD_PROJECT")
    return Path(named).resolve() if named else Path.cwd().resolve()


def project_checkout() -> Path:
    """The checkout holding the project being worked on. Sessions, the board, and every tool that finds
    ``.sessions/`` start here, so they all find the same one."""
    return checkout_holding(project_folder())


def board_checkout() -> Path:
    """The checkout whose ``.sessions/`` holds the board. A ticket's worktree is a linked worktree of the project, so
    a chat working there reads the same board as one in the main checkout."""
    return main_checkout_of(project_checkout())


@contextmanager
def working_on(project: Path | str) -> Iterator[Path]:
    """Run one call on ``project``: inside it, ``project_folder()`` is that folder and ``project_checkout()`` the
    checkout holding it. Each thread and each task keeps its own, so calls from different chats never see each other's
    project."""
    token = _called_project.set(Path(project).resolve())
    try:
        yield project_checkout()
    finally:
        _called_project.reset(token)


class WorkState:
    """The open branch, worktree, and session, shared by the repo and session commands."""

    def __init__(self, repo_root: Path | str) -> None:
        self.root = Path(repo_root).resolve()

    @property
    def sessions_folder(self) -> Path:
        return self.root / SESSIONS_FOLDER

    @property
    def path(self) -> Path:
        return self.sessions_folder / STATE_NAME

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
        """The release this checkout's work belongs to: the open session, else the branch, else ``main``."""
        return self.session or self.branch or "main"

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
