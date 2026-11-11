"""The open session of one chat, kept by the cdd server in ``~/.cdd/open-sessions.json``.

What is open is true only for one chat on one machine, so it is never written in the checkout, where it would be
committed and clash between worktrees. A call that names its chat keeps its own entry; a call that names none keeps one
entry for the checkout folder it works in."""
from __future__ import annotations

import threading
from pathlib import Path

from harness.installation.json_file import JsonFile
from harness.mcp.cdd_home import CddHome

SESSIONS_FOLDER = ".sessions"
OPEN_SESSIONS_NAME = "open-sessions.json"
E2E_RESULTS_FOLDER = "e2e-test-results"
# A chat id the server could not name is not a chat of its own.
_NO_CHAT = ("", "unknown")
_CHAT_KEY = "chat:"
_FOLDER_KEY = "folder:"
# Every chat's call reaches this one file in the one server process, so its read-change-write runs one at a time.
_WRITING = threading.Lock()


class WorkState:
    """The open session of one chat in the repository's own folder, or of one checkout folder for a call that names no
    chat; a chat in a ticket's own worktree works on that ticket whatever is kept here. Nothing it keeps is written under
    the checkout; ``sessions_folder`` is only where the checkout's sessions live."""

    def __init__(self, repo_root: Path | str, chat: str = "", home: Path | str | None = None) -> None:
        self.root = Path(repo_root).resolve()
        self.chat = "" if (chat or "").strip() in _NO_CHAT else chat.strip()
        self._file = JsonFile(Path(home).resolve() / OPEN_SESSIONS_NAME if home else CddHome().folder / OPEN_SESSIONS_NAME)

    @property
    def sessions_folder(self) -> Path:
        return self.root / SESSIONS_FOLDER

    @property
    def path(self) -> Path:
        """The file under ``~/.cdd`` that keeps every chat's open session."""
        return self._file.path

    @property
    def key(self) -> str:
        """This chat's entry in that file; a call naming no chat keeps the entry of its checkout folder."""
        return f"{_CHAT_KEY}{self.chat}" if self.chat else f"{_FOLDER_KEY}{self.root}"

    @property
    def session(self) -> str:
        return self._value("session")

    @session.setter
    def session(self, name: str) -> None:
        self._store("session", name)

    def load(self) -> dict[str, str]:
        entry = self._file.read().get(self.key, {})
        if not isinstance(entry, dict):
            return {}
        return {str(key): str(value) for key, value in entry.items() if str(value).strip()}

    def _value(self, key: str) -> str:
        return self.load().get(key, "").strip()

    def _store(self, key: str, value: str) -> None:
        cleaned = str(value or "").strip()
        with _WRITING:
            everything = self._file.read()
            entry = dict(everything.get(self.key) or {})
            if entry.get(key, "") == cleaned:
                return
            if cleaned:
                entry[key] = cleaned
            else:
                entry.pop(key, None)
            entry["folder"] = str(self.root)
            everything[self.key] = entry
            # WHY: a folder that is gone, such as a removed worktree or a spec's throwaway project, opens nothing again.
            kept = {name: held for name, held in everything.items() if not isinstance(held, dict) or Path(held.get("folder", "") or ".").exists()}
            self._file.write(kept)
