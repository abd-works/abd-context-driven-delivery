"""What each practice and each of its fidelities has in one session: where it writes, the files it declares, its graph."""

from __future__ import annotations

import json
import os
import re
from functools import cache
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Callable

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.installation.destination import data_field, identity, language_adapter
from harness.mcp.mcp_server import mcp
from harness.installation.context_config import CONTEXT_FOLDER, ContextConfig
from tools.file_manager.file_manager import FileEntry

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from harness.guidance.guidance import FidelityGuidance, GuidanceCollection, PracticeGuidance
    from space.session.session import Session

_OUTPUT_PATTERN_MARKS = {"*", "{"}
_REMEMBERED_FOLDERS_FILE = "practices.json"


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


class RememberedFolders:
    """The folders each practice reads in every session of one repository, kept in its ``.context/practices.json`` as
    sets of peer folders by practice key."""

    def __init__(self, repo_root: Path) -> None:
        self._path = Path(repo_root) / CONTEXT_FOLDER / _REMEMBERED_FOLDERS_FILE

    def of(self, practice: str) -> list[list[str]]:
        """The sets of folders remembered for practice; none when it reads its default folder."""
        return list(self._read().get(practice, []))

    def remember(self, practice: str, folders: list[list[str]]) -> None:
        """Remember folders for practice; no folders forgets it, so it reads its default folder again."""
        stored = self._read()
        if folders:
            stored[practice] = folders
        else:
            stored.pop(practice, None)
        self._write(stored)

    def _read(self) -> dict:
        return json.loads(self._path.read_text(encoding="utf-8")) if self._path.is_file() else {}

    def _write(self, stored: dict) -> None:
        if not stored:
            self._path.unlink(missing_ok=True)
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(stored), encoding="utf-8")


@identity("session_file", "name")
@language_adapter(language="typescript")
@agent_toolset
class PracticeSessionOutput:
    """What one practice has in one session: its guideline, the paths it reads, its graph, whether it is on, the folder
    it writes under, and the files each of its fidelities declares."""

    # The guideline, folders, and graph load on first use: the board asks every ticket's session
    # which practices are enabled after every cdd call, and that question needs none of them.

    def __init__(self, name: str, session: Session) -> None:
        self._name = name
        self._session = session
        self._guideline: PracticeGuidance | None = None
        self._output_paths: list | None = None
        self._graph: Graph | None = None

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str, project: Path) -> PracticeSessionOutput:
        """The practice named practice in the session whose session.json is session, a path from project, the project
        the tool call names."""
        # WHY: Session makes its PracticeSessionOutput objects from this module, so Session is imported when first loaded.
        from space.session.session import Session

        return Session.from_file(session, project).practice(practice)

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
    def guideline(self) -> PracticeGuidance:
        """This session's own copy of the practice's guidance, which knows the session, so each of its fidelities can
        find the files it declares in this session."""
        if self._guideline is None:
            self.guideline = PracticeCatalogue.create(self.name)
        return self._guideline

    @guideline.setter
    def guideline(self, guidance: PracticeGuidance) -> None:
        """Work with guidance, the practice an action was given, at its fidelity; it now works in this session, and
        each of its fidelities holds what it has in this session, so it answers its outputs and files itself."""
        guidance._attach_workspace(workspace=self._session)
        for fidelity in guidance.fidelities:
            fidelity.session_output = FidelitySessionOutput(self, fidelity)
        self._guideline = guidance

    @property
    def fidelities(self) -> GuidanceCollection:
        """The practice's fidelities, such as story_map, by name, each able to list its files in this session."""
        return self.guideline.fidelities

    @property
    def _remembered(self) -> RememberedFolders:
        return RememberedFolders(self._session.repo_from_session())

    @property
    def _folders(self) -> list:
        """The sets of peer folders this practice reads in the session: the ones remembered for the repository, else
        its default folder. Callers ask for its graph or its log line instead, so how the folders are kept stays this
        class's own."""
        if self._output_paths is None:
            self._output_paths = self._remembered.of(self.name) or [[str(self._default_folder)]]
        return self._output_paths

    @property
    def folders(self) -> list[Path]:
        """Every folder this practice reads in the session, in order: what an action's log line names it worked on."""
        return [Path(folder).resolve() for group in self._folders for folder in group]

    def remember_folders(self, folders: list[list[Path]]) -> None:
        """Read this practice from folders, sets of peer folders, in every session of the repository, kept in its
        ``.context/practices.json``. Folders that are the default are not kept, so a later default still applies."""
        normalized = [[str(Path(item).resolve()) for item in group] for group in folders]
        is_default = normalized == [[str(self._default_folder)]]
        self._remembered.remember(self.name, [] if is_default else normalized)
        self._output_paths = None
        self._graph = None

    @property
    def graph(self) -> Graph:
        """This practice's graph, built once from its first folder, with its saved graph in the session's repository."""
        if self._graph is None:
            from harness.graph.graph import Graph

            primary = Path(self._folders[0][0])
            self._graph = Graph.of_practice(self._session.repo_path, self.name, primary)
        return self._graph

    @property
    def root_node_name(self) -> str:
        """The name of the root node of this practice's graph, which an action's log line names; empty when its graph
        holds no such practice."""
        practice = self.graph.practices.get(self.name)
        return practice.root_node.name if practice is not None else ""

    @property
    def _saved(self) -> dict:
        """What session.json keeps for this practice: whether it is on, and the format each fidelity was last given."""
        return dict(self._session.fields.get("practices", {}).get(self.name, {}))

    def _save(self, **values: object) -> None:
        saved = self._session.fields.get("practices", {})
        self._session.save_fields(practices={**saved, self.name: {**self._saved, **values}})

    @property
    @data_field
    def enabled(self) -> bool:
        """Whether the session works on this practice: true until a person turns it off."""
        return self._saved.get("enabled", True)

    @mcp
    @agent_tool
    @noSessionLog
    def enable(self, is_enabled: bool) -> PracticeSessionOutput:
        """Turn this practice on or off for its session, saved in its session.json."""
        self._save(enabled=is_enabled)
        return self

    @property
    def working_fidelity(self) -> str:
        """The name of the fidelity this practice works at in the session, such as story_map; empty when it has none."""
        current = getattr(self.guideline.fidelities, "current", None)
        return str(current.name) if current is not None else ""

    @property
    def working_format(self) -> str:
        """The format this practice works in, such as drawio; empty when it has none."""
        return str(getattr(self.guideline, "format", "") or "")

    def keep_format(self) -> None:
        """Save the format this practice works in as its current fidelity's, so the next action on that fidelity in
        this session works in it without being told."""
        fidelity = self.working_fidelity
        if fidelity and self.guideline.format:
            self._save(formats={**self._saved.get("formats", {}), fidelity: self.guideline.format})

    def use_kept_format(self) -> None:
        """Work in the format last kept for the current fidelity; the fidelity's own format when none was kept."""
        kept = self._saved.get("formats", {}).get(self.working_fidelity, "")
        if kept:
            self.guideline.format = kept

    def log_validation(self, violations: list[str]) -> None:
        """Log a validate of this practice at its working fidelity in its session's log, with each violation's
        synopsis; no violations is a validate that passed."""
        detail = " ".join(violations)
        self._session.log.line(f"validate {type(self.guideline).__name__} {self.working_fidelity} {detail}".rstrip())

    @property
    def _overrides(self) -> dict:
        """What session.json's ``outputs`` keeps for this practice: the root a person chose, and under a fidelity's name
        that fidelity's own root and a file name per format for a single-file output."""
        return dict(self._session.fields.get("outputs", {}).get(self.name, {}))

    def _save_overrides(self, overrides: dict) -> None:
        outputs = dict(self._session.fields.get("outputs", {}))
        self._session.save_fields(outputs={**outputs, self.name: overrides})

    @property
    def _configured_folder(self) -> str | None:
        """The folder the project's ``.context/config.json`` names for this practice, relative to the session's root."""
        return ContextConfig(self._session.repo_from_session()).practice_folder(self.name)

    @property
    def _default_folder(self) -> Path:
        """The session's root plus the folder the project's config names for this practice, else the practice's own
        default folder, such as src for BDD."""
        relative = self._configured_folder or getattr(self.guideline, "default_workspace_folder", None) or "."
        return (self._session.root / relative).resolve()

    @property
    def folder(self) -> Path:
        """The folder this practice writes under: the root a person chose, kept relative to the session's root, or its
        default folder."""
        chosen = self._overrides.get("root")
        return (self._session.root / chosen).resolve() if chosen else self._default_folder

    @property
    def output_root(self) -> Path:
        """The folder this practice's fidelities declare their outputs under: the root a person chose, else the folder
        the project's config names, else the session's root. Unlike ``folder`` it never adds the practice's own default
        folder, since a declared output such as `.context/story-map.md` or `**/*_spec.py` is written from the workpath."""
        chosen = self._overrides.get("root") or self._configured_folder
        return (self._session.root / chosen).resolve() if chosen else self._session.root

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
        return bool(self._overrides.get("root"))

    @mcp
    @agent_tool
    @noSessionLog
    def choose_root(self, path: str) -> PracticeSessionOutput:
        """Write this practice's files under path, a folder in the repository."""
        self.keep_root(self._session.repo_from_session() / path)
        return self

    def keep_root(self, root: Path) -> None:
        """Write this practice's files under root, kept in session.json relative to the workpath, so the root still
        names the same folder after the workpath moves."""
        # A practice root holds the practice's code; its documents and diagrams go in the root's own .context.
        if CONTEXT_FOLDER in Path(root).parts:
            raise PracticeRootInContextError(self.name, Path(root))
        relative = os.path.relpath(Path(root).resolve(), self._session.root)
        self._save_overrides({**self._overrides, "root": Path(relative).as_posix()})

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_root(self) -> PracticeSessionOutput:
        """Write this practice's files under its default root again: the workpath plus the practice's own folder."""
        self._save_overrides({key: value for key, value in self._overrides.items() if key != "root"})
        return self

    def output_overrides(self, fidelity: str) -> dict:
        """What session.json's ``outputs`` keeps for fidelity, one of this practice's: its own root and a file name per
        format for a single-file output."""
        return dict(self._overrides.get(fidelity, {}))


class FidelitySessionOutput:
    """What one fidelity of a practice has in one session: where it writes each format, the files it declares there,
    and the folder its validation reports go in."""

    def __init__(self, practice: PracticeSessionOutput, fidelity: FidelityGuidance) -> None:
        self._practice = practice
        self._fidelity = fidelity

    @property
    def _session(self) -> Session:
        return self._practice.session

    @property
    def reports_folder(self) -> Path:
        return self._session.reports_folder

    def output_paths(self) -> dict[str, list[str]]:
        """Where this fidelity writes each format in the session: its declared paths under its own root when
        session.json names one, else under its practice's output root. session.json can also name a file per format
        for a single-file output."""
        overrides = self._practice.output_overrides(str(self._fidelity.name))
        chosen = overrides.get("root")
        root = (self._session.root / chosen).resolve() if chosen else self._practice.output_root
        return {
            label: [_output_path(root, name) for name in _output_names(declared, overrides.get(label))]
            for label, declared in self._fidelity.outputs.items()
        }

    def files(self) -> dict[str, list[FileEntry]]:
        """The files this fidelity declares in the session, by format, each with its path from the project and whether
        it exists. A pattern lists the files the session worked on, not every match in the repository."""
        # Asking git what the branch changed is slow, and a project that is no repository has no branch, so it is asked
        # only once a pattern finds files.
        worked_on = cache(self._session.session_files.worked_on)
        return {label: [entry for path in paths for entry in self._declared_files(path, worked_on)] for label, paths in self.output_paths().items()}

    def has_output(self) -> bool:
        """Whether a file this fidelity declares is already in the session, such as one a person wrote. Unlike
        ``files`` it never asks git: a pattern counts only in a session with a folder of its own, since on the whole
        repository a pattern also finds other sessions' files, and the board asks this of every fidelity."""
        repo = self._session.repo
        own_folder = self._session.root != repo.root
        for paths in self.output_paths().values():
            for declared in paths:
                pattern = _named_parts_as_wildcards(repo.path_from_top(declared))
                if "*" not in pattern and (repo.root / pattern).exists():
                    return True
                if "*" in pattern and own_folder and repo.file_manager.find(pattern):
                    return True
        return False

    def _declared_files(self, declared: str, worked_on: Callable[[], set[Path] | None]) -> list[FileEntry]:
        """A declared path, or each file of this session's that a pattern finds; a pattern that finds none stays as
        written, not yet there."""
        repo = self._session.repo
        relative = repo.path_from_top(declared)
        pattern = _named_parts_as_wildcards(relative)
        if "*" not in pattern:
            return [FileEntry(relative, (repo.root / relative).exists())]
        found = repo.file_manager.find(pattern)
        mine = worked_on() if found else None
        found = [path for path in found if mine is None or path.resolve() in mine]
        return [FileEntry(repo.path_from_top(path), True) for path in found] or [FileEntry(relative, False)]


def _output_names(declared: str | list[str], override: str | None) -> list[str]:
    """The file names a declared output writes: override in place of the declared name for a single-file output."""
    names = [declared] if isinstance(declared, str) else list(declared)
    is_single_file = len(names) == 1 and not set(names[0]) & _OUTPUT_PATTERN_MARKS
    return [PurePosixPath(names[0]).with_name(override).as_posix()] if override and is_single_file else names


def _output_path(root: Path, name: str) -> str:
    folder_mark = "/" if name.endswith("/") else ""
    return f"{(root / name).as_posix()}{folder_mark}"


def _named_parts_as_wildcards(path: str) -> str:
    """A declared path with its named parts, such as `{module}/{module}-model.md`, as a pattern. A named folder can be
    a module several folders deep, so it matches folders at any depth; a named part of a file name matches within it."""
    folders = re.sub(r"\{[^{}/]+\}/", "**/", path)
    return re.sub(r"\{[^{}/]+\}", "*", folders)
