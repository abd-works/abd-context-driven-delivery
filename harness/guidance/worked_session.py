"""What guidance and the guidance actions ask of the session they work in. space/session's *Session*,
*PracticeSessionOutput* and *FidelitySessionOutput* answer these questions; space/session imports the framework, so the
framework names each by the questions it asks of it, extending the *CallSession* every call works in, as the action
catalogue names the fidelity an action runs on (*WorkedFidelity*)."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from harness.agent_tools.tool_call import CallSession

if TYPE_CHECKING:
    from harness.agent_tools.chat_pointer import ChatPointer
    from harness.guidance.guidance import FidelityGuidance

# The files a call names: one path, several, or none, written from the project's root or absolute.
NamedPaths = list[str] | str | None


class _SessionFiles(Protocol):
    """The files under a session's root, which the session finds for guidance."""

    def find(self, pattern: str) -> list[Path]:
        """Each file under the session's root that the glob pattern matches."""

    def from_root(self, entry: str) -> str:
        """A path a listing names, written from the session's root."""


class _SessionPaths(Protocol):
    """The paths of a session's project, which read the document a call names."""

    def document_named(self, content: str = "", paths: NamedPaths = None) -> str:
        """The text content holds, or the files at paths, read from the session's project."""

    def path_named(self, named: str | Path) -> Path:
        """The path a call names, read from the session's project."""


class _InjectedRules(Protocol):
    """The rules a session's log holds until its next line names them."""

    def note(self, rules: object, path: str) -> None:
        """Hold rules as given to the agent after it edited the file at path."""


class _SessionLog(Protocol):
    """A session's log, which names the rules the agent was given after each edit."""

    @property
    def injected_rules(self) -> _InjectedRules:
        """The rules given since the log's last line."""

    def by(self, chat: ChatPointer | None) -> object:
        """The log as one chat writes it, each line pointing at that chat."""


class _SessionRecord(Protocol):
    """A session's record, the session.json it keeps, whose typed fields write themselves as a dict."""

    @property
    def fields(self) -> object:
        """The record's fields."""


class _TestTiers(Protocol):
    """The test tiers a session records for each module, each tier with its test tool."""

    @property
    def recorded(self) -> Mapping[str, Mapping[str, str]]:
        """Each module's tiers, by the module's path from the project."""

    def of(self, module: str) -> Mapping[str, str]:
        """The tiers module uses, each with its test tool."""

    def record(self, module: str, tiers: dict[str, str]) -> Mapping[str, str]:
        """Keep tiers beside the tiers module already holds, and answer the module's tiers."""


class _SessionCheckout(Protocol):
    """The one checkout a session works in."""

    @property
    def root(self) -> Path:
        """The top folder of the session's one project."""


class WorkedSession(CallSession, Protocol):
    """The session a practice or a guidance action works in: its name and record, the checkout it works in, the folder
    it works in, its paths, which read the document a call names from its project, the files under its root, its log,
    which notes the rules an edit was checked against, the practices it works on, and its graph."""

    @property
    def name(self) -> str:
        """The session's name."""

    @property
    def checkout(self) -> _SessionCheckout:
        """The one checkout the session works in."""

    @property
    def session_file(self) -> Path:
        """Its session.json."""

    @property
    def record_folder(self) -> Path:
        """The folder of its record on main."""

    @property
    def overlays(self) -> list[str]:
        """The patterns it overlays on its graph, by name."""

    @property
    def stories(self) -> Sequence[str]:
        """The stories its idea file names."""

    @property
    def record(self) -> _SessionRecord:
        """Its session.json."""

    @property
    def test_tiers(self) -> _TestTiers:
        """The test tiers it records for each module."""

    @property
    def practices(self) -> Mapping[str, PracticeOutput]:
        """The practices it works on, by key."""

    @property
    def graph(self) -> object:
        """Its knowledge graph, typed as *Graph* only inside harness/graph."""

    def choose_overlays(self, overlays: list[str]) -> None:
        """Overlay the patterns named on its graph from now on."""

    def practice(self, key: str) -> PracticeOutput:
        """The practice whose key is key, on or off for the session."""

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


class WrittenOutput(Protocol):
    """The files one fidelity writes in a session: where each format goes, which are there, where a render of one of
    them is saved, and which a person reviews."""

    def output_paths(self) -> dict[str, list[str]]:
        """Where the fidelity writes each format in the session."""

    def files(self) -> dict[str, list[SessionFile]]:
        """The files the fidelity declares in the session, by format."""

    def has_output(self) -> bool:
        """Whether a file the fidelity declares is already in the session."""

    def saved_beside(self, source: Path, format: str) -> Path | None:
        """Where a render of the file at source into format is saved in the session."""

    def files_to_review(self) -> dict[str, list[SessionFile]]:
        """The files a person reviews for the fidelity, by format."""

    def every_file(self) -> list[Path]:
        """Every file the fidelity declares that is in the session."""


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
    def written(self) -> WrittenOutput:
        """The files the fidelity writes in the session."""


class _NoWrittenFiles:
    """The files a fidelity writes in no session: none."""

    def output_paths(self) -> dict[str, list[str]]:
        return {}

    def files(self) -> dict[str, list[SessionFile]]:
        return {}

    def every_file(self) -> list[Path]:
        return []

    def has_output(self) -> bool:
        return False

    def saved_beside(self, source: Path, format: str) -> Path | None:
        return None

    def files_to_review(self) -> dict[str, list[SessionFile]]:
        return {}


class NoSessionOutput:
    """What a fidelity has while its practice works in no session: no format chosen, no root, and no file written, so a
    caller asks the same questions in a session or out of one and is never handed none."""

    chosen_formats: list[str] = []
    roots: list[Path] = []
    written = _NoWrittenFiles()

    def choose_format(self, format: str, is_chosen: bool) -> object:
        """Nothing is chosen outside a session."""
        return self


NO_SESSION_OUTPUT = NoSessionOutput()


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
