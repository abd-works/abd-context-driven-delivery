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


class WorkedSession(Protocol):
    """The session a practice works in: it reads the document a call names from its project, and finds the files under
    its root."""

    @property
    def work_root(self) -> Path:
        """The folder the session works in."""

    @property
    def session_files(self) -> _SessionFiles:
        """The files under the session's root."""

    def document_named(self, content: str = "", paths: NamedPaths = None) -> str:
        """The text content holds, or the files at paths, read from the session's project."""


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

    def output_paths(self) -> dict[str, list[str]]:
        """Where the fidelity writes each format in the session."""

    def files(self) -> dict[str, list]:
        """The files the fidelity declares in the session, by format."""

    def has_output(self) -> bool:
        """Whether a file the fidelity declares is already in the session."""


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
