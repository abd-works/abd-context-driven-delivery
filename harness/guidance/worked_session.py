"""What guidance asks of the session it works in. space/session's *Session*, *PracticeSessionOutput* and
*FidelitySessionOutput* answer these questions; harness imports nothing from space, so guidance names each by the
questions it asks of it, as the action catalogue names the fidelity an action runs on (*WorkedFidelity*)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance

# The files a call names: one path, several, or none, written from the project's root or absolute.
NamedPaths = list[str] | str | None


class _SessionFiles(Protocol):
    """The files under a session's root, which the session finds for guidance."""

    def find(self, pattern: str) -> list[Path]:
        """Each file under the session's root that the glob pattern matches."""


class _SessionPaths(Protocol):
    """The paths of a session's project, which read the document a call names."""

    def document_named(self, content: str = "", paths: NamedPaths = None) -> str:
        """The text content holds, or the files at paths, read from the session's project."""


class _InjectedRules(Protocol):
    """The rules a session's log holds until its next line names them."""

    def note(self, rules: object, path: str) -> None:
        """Hold rules as given to the agent after it edited the file at path."""


class _SessionLog(Protocol):
    """A session's log, which names the rules the agent was given after each edit."""

    @property
    def injected_rules(self) -> _InjectedRules:
        """The rules given since the log's last line."""


class WorkedSession(Protocol):
    """The session a practice works in: its paths read the document a call names from its project, it finds the files
    under its root, and its log notes the rules an edit was checked against."""

    @property
    def work_root(self) -> Path:
        """The folder the session works in."""

    @property
    def session_files(self) -> _SessionFiles:
        """The files under the session's root."""

    @property
    def paths(self) -> _SessionPaths:
        """The paths of the session's project."""

    @property
    def log(self) -> _SessionLog:
        """The session's log."""


class SessionFile(Protocol):
    """One file a fidelity declares in a session, as space/session's *FileEntry* answers it."""

    @property
    def path(self) -> str:
        """The file's path from the project."""


class _WrittenFiles(Protocol):
    """The files one fidelity writes in a session."""

    def output_paths(self) -> dict[str, list[str]]:
        """Where the fidelity writes each format in the session."""

    def files(self) -> dict[str, list[SessionFile]]:
        """The files the fidelity declares in the session, by format."""

    def has_output(self) -> bool:
        """Whether a file the fidelity declares is already in the session."""


class FidelityOutput(Protocol):
    """What one fidelity has in the session its practice works in: the formats chosen for it there, and the files it
    declares there."""

    @property
    def chosen_formats(self) -> list[str]:
        """The formats chosen for the fidelity in the session, in the order they were chosen."""

    def choose_format(self, format: str, is_chosen: bool) -> object:
        """Choose format for the fidelity in the session, or stop choosing it."""

    @property
    def roots(self) -> list[Path]:
        """The folders the fidelity writes under in the session."""

    @property
    def written(self) -> _WrittenFiles:
        """The files the fidelity writes in the session."""


class PracticeOutput(Protocol):
    """What one practice has in the session it works in: the session, the folder it writes in there, and what each of
    its fidelities has there."""

    @property
    def session(self) -> WorkedSession:
        """The session the practice works in."""

    @property
    def folder(self) -> Path:
        """The folder the session names for the practice."""

    def of_fidelity(self, fidelity: FidelityGuidance) -> FidelityOutput:
        """What fidelity has in the session."""
