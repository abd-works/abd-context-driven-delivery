"""SessionRecord - one session's ``session.json``: what it holds, and each change to it saved on main."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.installation.json_file import HeldJsonFile, JsonFile
from space.session.answer_reads import ANSWER_READS, HeldForAnswer

if TYPE_CHECKING:
    from space.session.session import Session

SESSION_FILE = "session.json"
# How much of a saved value a save's commit message shows: a workpath or a list can be long.
_SHOWN_CHARACTERS = 40


class SessionRecord:
    """The ``session.json`` in one session's folder, which holds its title, scope, parent, tags, workpath, and practice
    roots. It is read once for each answer that asks (*AnswerReads*), and between answers again only once the file
    changes. Every change a session makes to its folder is queued to be saved on main through it, so its caller never
    waits for git."""

    def __init__(self, session: Session) -> None:
        self._session = session
        # Its session.json, read again only once the file changes; none before the session has a folder.
        self._held: HeldJsonFile | None = None
        # What its session.json holds, read once for each answer that asks.
        self._fields = HeldForAnswer[dict]()

    def kept_in(self, folder: Path | None) -> None:
        """Read the session.json of folder from now on, the session's folder since it was given one or moved."""
        self._held = HeldJsonFile(JsonFile(folder / SESSION_FILE)) if folder is not None else None
        self._fields.drop()

    @property
    def fields(self) -> dict:
        """What ``session.json`` holds, read once for each answer that asks; nothing before the session has a folder."""
        held = self._held
        if held is None:
            return {}
        return dict(self._fields.get(self._session.answer, held.read))

    @property
    def fields_on_disk(self) -> dict:
        """What ``session.json`` holds now, read past this answer's reads: another call changes it."""
        return self._held.read() if self._held is not None else {}

    def read_again(self) -> None:
        """Forget what this answer read, so the next ask reads the file."""
        self._fields.drop()

    def save_fields(self, **values: object) -> None:
        """Merge ``values`` into ``session.json``, keeping what others store there, and make the session's folder when
        it has none yet, as a project's main session has none until something is saved in it. It merges into what the
        file holds now, not what this answer read, and begins a new answer, so no read in this process answers what the
        file held before."""
        file = self._held if self._held is not None else JsonFile(self._session.session_file)
        try:
            file.write({**file.read(), **values})
        finally:
            self._fields.drop()
            ANSWER_READS.begin()
        self.saved(", ".join(f"{name} {self._shown(str(value))}" for name, value in values.items()))

    def save(self) -> None:
        """Save the session's name, workpath, and repository, creating its folder, and keep the fields others store
        there, such as a board ticket's title, scope, and parent."""
        session = self._session
        if session.record_folder is None:
            return
        self.save_fields(name=session.name, workpath=session.workpath_from_checkout, repo_path=str(session.repo_path))

    def saved(self, change: str) -> None:
        """Queue the save on main of change to the session, such as ``stage Specification``: every change to a session
        is kept on main for every chat and worktree, committed and pushed on the saving thread."""
        self._session.sessions.saves.later(f"sessions: {self._session.name} {change}")

    def _shown(self, text: str) -> str:
        """A saved value as a commit message names it, cut short."""
        return text if len(text) <= _SHOWN_CHARACTERS else f"{text[:_SHOWN_CHARACTERS]}…"
