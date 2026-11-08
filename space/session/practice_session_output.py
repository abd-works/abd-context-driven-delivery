"""What each practice and each of its fidelities has in one session: where it writes and the files it declares."""

from __future__ import annotations

import os
from functools import cache
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Callable

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.declared_file import DeclaredFile
from harness.installation.destination import data_field, identity, language_adapter
from harness.mcp.mcp_server import mcp
from harness.installation.context_config import CONTEXT_FOLDER
from space.session.file_manager import FileEntry

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, GuidanceCollection, PracticeGuidance
    from space.session.session import Session

_OUTPUT_PATTERN_MARKS = {"*", "{"}


class PracticeRootInContextError(ValueError):
    """A practice root was chosen inside a ``.context`` folder, which would put the practice's code among its documents
    and its documents in a ``.context`` within a ``.context``. It names the practice and the folder it refused."""

    def __init__(self, practice: str, root: Path) -> None:
        self.practice = practice
        self.root = root
        super().__init__(
            f"{root} is inside a .context folder: choose the folder for {practice}'s code, "
            "and its documents and diagrams go in that folder's .context"
        )


@identity("session_file", "name")
@language_adapter(language="typescript")
@agent_toolset
class PracticeSessionOutput:
    """What one practice has in one session: the session's own instance of the practice, which the session's graph
    holds too, whether it is on, the folder it writes under, and the files each of its fidelities declares."""

    def __init__(self, guidance: PracticeGuidance, session: Session) -> None:
        self._guidance = guidance
        self._name = guidance.key
        self._session = session

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str, call: ToolCall) -> PracticeSessionOutput:
        """The practice named practice in the session whose session.json is session, a path from the project the call
        names."""
        return call.session_named(session).practice(practice)

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    def session(self) -> Session:
        return self._session

    @property
    @data_field
    def session_file(self) -> str:
        """Its session's session.json as a path from the project, which names the session this practice is in."""
        return self._session.session_file_from_project

    @property
    def guidance(self) -> PracticeGuidance:
        """The session's one instance of the practice: the one its graph holds and its actions work with. It works in
        this session, so each of its fidelities finds the files it declares here."""
        return self._guidance

    def of_fidelity(self, fidelity: FidelityGuidance) -> FidelitySessionOutput:
        """What fidelity, one of this practice's, has in this session."""
        return FidelitySessionOutput(self, fidelity)

    @property
    def fidelities(self) -> GuidanceCollection:
        """The practice's fidelities, such as story_map, by name, each able to list its files in this session."""
        return self._guidance.fidelities

    @property
    def saved(self) -> dict:
        """What session.json's ``practices`` keeps for this practice: whether it is on, and the format each fidelity was
        last given, which each fidelity's FidelitySessionOutput reads and saves for itself."""
        return dict(self._session.fields.get("practices", {}).get(self.name, {}))

    def save(self, **values: object) -> None:
        """Merge values into what session.json's ``practices`` keeps for this practice."""
        saved = self._session.fields.get("practices", {})
        self._session.save_fields(practices={**saved, self.name: {**self.saved, **values}})

    @property
    @data_field
    def enabled(self) -> bool:
        """Whether the session works on this practice: true until a person turns it off."""
        return self.saved.get("enabled", True)

    @mcp
    @agent_tool
    @noSessionLog
    def enable(self, is_enabled: bool) -> PracticeSessionOutput:
        """Turn this practice on or off for its session, saved in its session.json."""
        self.save(enabled=is_enabled)
        return self

    @property
    def _current_fidelity(self) -> FidelityGuidance | None:
        return self._guidance.fidelities.current

    @property
    def working_fidelity(self) -> str:
        """The name of the fidelity this practice works at in the session, such as story_map; empty when it has none."""
        current = self._current_fidelity
        return str(current.name) if current is not None else ""

    @property
    def working_format(self) -> str:
        """The format this practice works in, such as drawio: its current fidelity's; empty when it has none."""
        return self._guidance.format or ""

    @property
    def chosen_outputs(self) -> dict:
        """What session.json's ``outputs`` keeps for this practice: the root a person chose, and under each fidelity's
        name what that fidelity keeps for itself."""
        return dict(self._session.fields.get("outputs", {}).get(self.name, {}))

    def _save_chosen_outputs(self, chosen: dict) -> None:
        outputs = dict(self._session.fields.get("outputs", {}))
        self._session.save_fields(outputs={**outputs, self.name: chosen})

    @property
    def _chosen_or_configured_root(self) -> str | None:
        """Where this practice writes, relative to the session's root, when someone said: the root a person chose in
        this session, else the folder the project's ``.context/config.json`` names for the practice."""
        return self.chosen_outputs.get("root") or self._session.context_config.practice_folder(self.name)

    @property
    def folder(self) -> Path:
        """The folder this practice writes its code under: the root chosen or configured,
        else the practice's own default folder under the session's root, such as src for BDD."""
        relative = self._chosen_or_configured_root or self._guidance.default_workspace_folder
        return (self._session.work_root / relative).resolve()

    @property
    def output_root(self) -> Path:
        """The folder this practice's fidelities declare their outputs under: the root chosen or configured, else the
        session's root itself. A declared output such as `.context/story-map.md` or `**/*_spec.py` is named from the
        workpath, so the practice's own default folder is not added."""
        return (self._session.work_root / (self._chosen_or_configured_root or ".")).resolve()

    @property
    @data_field
    def root(self) -> str:
        """The folder this practice writes under, as a path from the project: the one a person chose, or the
        workpath plus the practice's default folder."""
        return self._session.from_project(self.folder)

    @property
    @data_field
    def is_root_chosen(self) -> bool:
        """Whether a person chose this practice's root, rather than it being the default."""
        return bool(self.chosen_outputs.get("root"))

    @mcp
    @agent_tool
    @noSessionLog
    def choose_root(self, path: str) -> PracticeSessionOutput:
        """Write this practice's files under path, a folder in the repository."""
        self.keep_root(self._session.repo_path / path)
        return self

    def keep_root(self, root: Path) -> None:
        """Write this practice's files under root, kept in session.json relative to the workpath, so the root still
        names the same folder after the workpath moves."""
        # A practice root holds the practice's code; its documents and diagrams go in the root's own .context.
        if CONTEXT_FOLDER in Path(root).parts:
            raise PracticeRootInContextError(self.name, Path(root))
        relative = os.path.relpath(Path(root).resolve(), self._session.work_root)
        self._save_chosen_outputs({**self.chosen_outputs, "root": Path(relative).as_posix()})

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_root(self) -> PracticeSessionOutput:
        """Write this practice's files under its default root again: the workpath plus the practice's own folder."""
        self._save_chosen_outputs({key: value for key, value in self.chosen_outputs.items() if key != "root"})
        return self


class FidelitySessionOutput:
    """What one fidelity of a practice has in one session: where it writes each format, the files it declares there,
    the format it was last given, and the folder its validation reports go in. It reads and saves its own part of
    session.json, which its practice keeps under the fidelity's name."""

    def __init__(self, practice: PracticeSessionOutput, fidelity: FidelityGuidance) -> None:
        self._practice = practice
        self._fidelity = fidelity

    @property
    def _session(self) -> Session:
        return self._practice.session

    @property
    def reports_folder(self) -> Path:
        return self._session.reports_folder

    @property
    def _chosen(self) -> dict:
        """What session.json's ``outputs`` keeps for this fidelity: its own root, and a file name per format for a
        single-file output."""
        return dict(self._practice.chosen_outputs.get(self._fidelity.name, {}))

    @property
    def root(self) -> Path:
        """The folder this fidelity writes under: its own root when session.json names one, else its practice's output
        root."""
        chosen = self._chosen.get("root")
        return (self._session.work_root / chosen).resolve() if chosen else self._practice.output_root

    @property
    def kept_format(self) -> str:
        """The format this fidelity was last given in the session; empty when none was kept."""
        return self._practice.saved.get("formats", {}).get(self._fidelity.name, "")

    def keep_format(self, format: str) -> None:
        """Keep format as the one this fidelity works in, so the next action on it in the session works in it."""
        self._practice.save(formats={**self._practice.saved.get("formats", {}), self._fidelity.name: format})

    def output_paths(self) -> dict[str, list[str]]:
        """Where this fidelity writes each format in the session: its declared paths under its root. session.json can
        name a file per format for a single-file output."""
        chosen = self._chosen
        return {
            label: [self._under_root(name) for name in self._output_names(declared, chosen.get(label))]
            for label, declared in self._fidelity.outputs.items()
        }

    def files(self) -> dict[str, list[FileEntry]]:
        """The files this fidelity declares in the session, by format, each with its path from the project and whether
        it exists. A pattern lists the files the session worked on, not every match in the repository."""
        # Asking git what the branch changed is slow, and a project that is no repository has no branch, so it is asked
        # only once a pattern finds files.
        worked_on = cache(self._session.session_files.worked_on)
        return {
            label: [entry for path in paths for entry in self._declared_files(label, path, worked_on)]
            for label, paths in self.output_paths().items()
        }

    def has_output(self) -> bool:
        """Whether a file this fidelity declares is already in the session, such as one a person wrote. Unlike
        ``files`` it never asks git: a pattern counts only in a session with a folder of its own, since on the whole
        repository a pattern also finds other sessions' files, and the board asks this of every fidelity."""
        own_folder = self._session.work_root != self._session.repo.root
        declared = [(label, self._declared(path)) for label, paths in self.output_paths().items() for path in paths]
        return any(self._exists(label, file) for label, file in declared if own_folder or file.names_one_path)

    def _declared(self, path: str) -> DeclaredFile:
        """A declared path under this fidelity's root, as a path from the project."""
        return DeclaredFile(self._session.repo.path_from_top(path))

    def _declared_files(self, label: str, path: str, worked_on: Callable[[], set[Path] | None]) -> list[FileEntry]:
        """A declared path, or each file of this session's that the fidelity declares where a pattern searches; a
        pattern that finds none stays as its search, not yet there."""
        repo = self._session.repo
        declared = self._declared(path)
        if declared.names_one_path:
            return [FileEntry(declared.glob, (repo.root / declared.glob).exists())]
        found = self._found(label, declared)
        mine = worked_on() if found else None
        found = [file for file in found if mine is None or file.resolve() in mine]
        return [FileEntry(repo.path_from_top(file), True) for file in found] or [FileEntry(declared.glob, False)]

    def _found(self, label: str, declared: DeclaredFile) -> list[Path]:
        """The files a declared pattern's search finds that this fidelity declares in the format label: a name used
        twice in one declared path must be the same text both times."""
        return [file for file in self._session.session_files.find(declared.glob) if self._fidelity.declares(file.as_posix(), label)]

    def _exists(self, label: str, declared: DeclaredFile) -> bool:
        """Whether a file the declared path names is in the repository."""
        if declared.names_one_path:
            return (self._session.repo.root / declared.glob).exists()
        return bool(self._found(label, declared))

    def _output_names(self, declared: str | list[str], chosen_name: str | None) -> list[str]:
        """The file names a declared output writes: the chosen name in place of the declared one for a single-file
        output."""
        names = [declared] if isinstance(declared, str) else list(declared)
        is_single_file = len(names) == 1 and not set(names[0]) & _OUTPUT_PATTERN_MARKS
        return [PurePosixPath(names[0]).with_name(chosen_name).as_posix()] if chosen_name and is_single_file else names

    def _under_root(self, name: str) -> str:
        folder_mark = "/" if name.endswith("/") else ""
        return f"{(self.root / name).as_posix()}{folder_mark}"
