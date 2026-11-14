"""What each practice and each of its fidelities has in one session: where it writes and the files it declares."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import cache
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Callable

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.design_canvas.versions import CanvasVersions
from harness.guidance.guidance import DeclaredFile
from harness.installation.data_class import data_field, identity, language_adapter
from harness.mcp.mcp_annotations import mcp
from harness.installation.context_config import CONTEXT_FOLDER
from harness.markdown.format import Format
from space.session.answer_reads import HeldForAnswer
from space.session.file_manager import FileEntry

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, GuidanceCollection, PracticeGuidance
    from space.session.session import Session

_OUTPUT_PATTERN_MARKS = {"*", "{"}
# A code format whose files also carry a second extension, such as React components in TypeScript; any other code format
# is its own extension alone.
_CODE_EXTENSIONS = {"typescript": (".ts", ".tsx"), "javascript": (".js", ".jsx")}
# Report and handoff names end with the time they were made, written so names sort by time.
REPORT_DATE_FORMAT = "%Y%m%dT%H%M%S"


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
        # The folder the project's ``.context/config.json`` names for this practice, read once for each answer.
        self._configured_folder = HeldForAnswer[str | None]()

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str, *, call: ToolCall) -> PracticeSessionOutput:
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
        """What session.json's ``practices`` keeps for this practice: whether it is on, and the formats chosen for each
        fidelity, which each fidelity's FidelitySessionOutput reads and saves for itself."""
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
        return self.chosen_outputs.get("root") or self._configured_folder.get(
            self._session.answer, lambda: self._session.context_config.practice_folder(self.name)
        )

    @property
    def folder(self) -> Path:
        """The folder this practice writes its code under: the root chosen or configured,
        else the practice's own default folder under the session's root, such as src for BDD."""
        relative = self._chosen_or_configured_root or self._guidance.default_workspace_folder
        return self._session.folder_under_root(relative)

    @property
    def output_root(self) -> Path:
        """The folder this practice's fidelities declare their outputs under: the root chosen or configured, else the
        session's root itself. A declared output such as `.context/story-map.md` or `**/*_spec.py` is named from the
        workpath, so the practice's own default folder is not added."""
        return self._session.folder_under_root(self._chosen_or_configured_root or ".")

    @property
    @data_field
    def design_view(self) -> str:
        """The Claude Design link recorded for the latest version of the design canvas kept under the folder this
        practice writes under (the UX practice's, ``CanvasVersions.in_practice_root``), which the chat bar's file viewer
        opens; empty while the practice is off or no link is recorded."""
        if not self.enabled:
            return ""
        canvas = CanvasVersions.in_practice_root(self.output_root)
        return canvas.link(canvas.latest) or ""

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
        relative = os.path.relpath(Path(root).resolve(), self._session.work_root)
        self._save_chosen_outputs({**self.chosen_outputs, "root": Path(relative).as_posix()})

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_root(self) -> PracticeSessionOutput:
        """Write this practice's files under its default root again: the workpath plus the practice's own folder."""
        self._save_chosen_outputs({key: value for key, value in self.chosen_outputs.items() if key != "root"})
        return self


class FormatNotOffered(ValueError):
    """A format was chosen for a fidelity that does not write it."""

    def __init__(self, fidelity: FidelityGuidance, format: str) -> None:
        super().__init__(f"{fidelity.name} does not write {format}; it writes {', '.join(fidelity.outputs) or 'nothing'}")
        self.fidelity = fidelity
        self.format = format


@identity("session_file", "practice_name", "name")
@language_adapter(language="typescript")
@agent_toolset
class FidelitySessionOutput:
    """What one fidelity of a practice has in one session: where it writes each format, the files it declares there,
    the formats chosen for it, and the folder its validation reports go in. It reads and saves its own part of
    session.json, which its practice keeps under the fidelity's name."""

    # chosen_formats only ever holds formats the fidelity offers, each once. The chat bar's chips, the board's chips
    # and the Story UI's toggles all change them through choose_format, so every page shows one choice.

    def __init__(self, practice: PracticeSessionOutput, fidelity: FidelityGuidance) -> None:
        self._practice = practice
        self._fidelity = fidelity

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str, fidelity: str, *, call: ToolCall) -> FidelitySessionOutput:
        """The fidelity named fidelity, such as story_map, of the practice named practice in the session whose
        session.json is session, a path from the project the call names."""
        return call.session_named(session).practice(practice).guidance.fidelities.entries[fidelity].session_output

    @property
    @data_field
    def session_file(self) -> str:
        """Its session's session.json as a path from the project, which names the session this fidelity is in."""
        return self._practice.session_file

    @property
    @data_field
    def practice_name(self) -> str:
        return self._practice.name

    @property
    @data_field
    def name(self) -> str:
        """The fidelity's name in its practice, such as story_map."""
        return self._fidelity.name

    @property
    @data_field
    def offered_formats(self) -> list[str]:
        """The formats this fidelity writes, in the order its practice declares them: what a person can choose."""
        return list(self._fidelity.outputs)

    @property
    @data_field
    def chosen_formats(self) -> list[str]:
        """The formats chosen for this fidelity in the session, in the order chosen: what a story map edit renders to
        and what a chip shows picked. Its default format until a person or an action chooses."""
        chosen = self._practice.saved.get("formats", {}).get(self._fidelity.name)
        if chosen is None:
            return [self._fidelity.default_format.name] if self._fidelity.default_format else []
        # A session saved before formats were chosen kept the one format its fidelity was last given.
        return [chosen] if isinstance(chosen, str) else list(chosen)

    @mcp
    @agent_tool
    @noSessionLog
    def choose_format(self, format: str, is_chosen: bool) -> FidelitySessionOutput:
        """Choose format for this fidelity in its session, or leave it out when is_chosen is false, saved in its
        session.json. A format the fidelity does not write is refused."""
        named = Format(format).name
        if named not in self.offered_formats:
            raise FormatNotOffered(self._fidelity, format)
        others = [each for each in self.chosen_formats if each != named]
        chosen = self.chosen_formats if is_chosen and named in self.chosen_formats else others + ([named] if is_chosen else [])
        self._practice.save(formats={**self._practice.saved.get("formats", {}), self._fidelity.name: chosen})
        return self

    @property
    def _session(self) -> Session:
        return self._practice.session

    # A line an action logs names what it worked on: the practice's name and folder, which the practice answers, and
    # the fidelity and the format it worked at, which the fidelity answers. An action hands the log this object.

    @property
    def practice(self) -> PracticeSessionOutput:
        """What its practice has in the session."""
        return self._practice

    @property
    def fidelity(self) -> FidelityGuidance:
        """The fidelity, which holds its name and the format it works in."""
        return self._fidelity

    @property
    def is_enabled(self) -> bool:
        """Whether the session works on this fidelity's practice."""
        return self._practice.enabled

    @property
    def reports_folder(self) -> Path:
        return self._session.reports_folder

    def reports(self) -> list[Path]:
        """This fidelity's validation reports in the session, oldest first: report names end with their date, which
        sorts by time."""
        folder = self.reports_folder
        return sorted(folder.glob(f"{self._fidelity.slug}-*.md")) if folder.is_dir() else []

    def new_report_path(self) -> Path:
        """Where a validation report of this fidelity made now is saved in the session."""
        folder = self.reports_folder
        folder.mkdir(parents=True, exist_ok=True)
        return folder / f"{self._fidelity.slug}-{datetime.now(timezone.utc).strftime(REPORT_DATE_FORMAT)}.md"

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
        return self._session.folder_under_root(chosen) if chosen else self._practice.output_root

    def output_paths(self) -> dict[str, list[str]]:
        """Where this fidelity writes each format in the session: its declared paths under its root. session.json can
        name a file per format for a single-file output."""
        chosen, root = self._chosen, self.root
        return {
            label: [self._under_root(name, root) for name in self._output_names(declared, chosen.get(label))]
            for label, declared in self._fidelity.outputs.items()
        }

    def files(self) -> dict[str, list[FileEntry]]:
        """The files this fidelity declares in the session, by format, each with its path from the project, whether it
        exists, and whether the session's branch changed it, so a page can show only the changed ones."""
        # Asking git what the branch changed is slow, so it is asked only once a file is there.
        changed = cache(self._session.session_files.changed)
        return {
            label: [entry for path in paths for entry in self._declared_files(label, path, changed)]
            for label, paths in self.output_paths().items()
        }

    def every_file(self) -> list[Path]:
        """Every file this fidelity declares that is in the session's checkout, worked on by the session or not: what a
        reader links to, such as each acceptance test of a story."""
        repo = self._session.repo
        found: list[Path] = []
        for label, paths in self.output_paths().items():
            for path in paths:
                declared = self._declared(path)
                named = [repo.root / declared.glob] if declared.names_one_path else self._found(label, declared)
                found += [file for file in named if file.is_file()]
        return found

    def has_output(self) -> bool:
        """Whether a file this fidelity declares is already in the session, such as one a person wrote. Unlike
        ``files`` it never asks git, and the board asks this of every fidelity."""
        return self.has_named_output() or self.has_found_output()

    def has_named_output(self) -> bool:
        """Whether a file this fidelity names by its whole path is there: one look each, quick enough for every read."""
        return any(self._exists(label, file) for label, file in self._declared_outputs() if file.names_one_path)

    def has_found_output(self) -> bool:
        """Whether a pattern this fidelity declares finds a file, which searches the session's folders: slow enough that
        the board keeps the answer. A pattern counts only in a session with a folder of its own, since on the whole
        repository a pattern also finds other sessions' files."""
        if self._session.work_root == self._session.repo.root:
            return False
        return any(self._exists(label, file) for label, file in self._declared_outputs() if not file.names_one_path)

    def _declared_outputs(self) -> list[tuple[str, DeclaredFile]]:
        return [(label, self._declared(path)) for label, paths in self.output_paths().items() for path in paths]

    def _declared(self, path: str) -> DeclaredFile:
        """A declared path under this fidelity's root, as a path from the project."""
        return DeclaredFile(self._session.repo.path_from_top(path))

    def _declared_files(self, label: str, path: str, changed: Callable[[], set[Path]]) -> list[FileEntry]:
        """A declared path, or each file the fidelity declares where a pattern searches, each marked when the session's
        branch changed it; a pattern that finds none stays as its search, not yet there."""
        repo = self._session.repo
        if path.endswith("/") and Format(label).is_code:
            return self._worked_on_code(label, changed)
        declared = self._declared(path)
        if declared.names_one_path:
            named = repo.root / declared.glob
            return [FileEntry(declared.glob, named.exists(), named.exists() and named.resolve() in changed())]
        found = self._found(label, declared)
        return [FileEntry(repo.path_from_top(file), True, file.resolve() in changed()) for file in found] or [FileEntry(declared.glob, False)]

    def _worked_on_code(self, label: str, changed: Callable[[], set[Path]]) -> list[FileEntry]:
        """The code a fidelity that declares a folder per module writes, such as Clean Engineering's ``{module}/``: the
        files in that format under its root that the session's branch changed, the code the ticket worked on, not every
        file of that language in the repository."""
        root = self.root.resolve()
        extensions = _CODE_EXTENSIONS.get(Format(label).name, (Format(label).extension,))
        worked_on = sorted(file for file in changed() if file.suffix in extensions and (file == root or root in file.parents))
        return [FileEntry(self._session.repo.path_from_top(file), file.exists(), True) for file in worked_on]

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

    def _under_root(self, name: str, root: Path) -> str:
        """A declared name under root, this fidelity's root. A root inside a ``.context`` folder, such as
        ``harness/.context/stories``, holds the practice's documents itself, so a declared ``.context/story-map.md``
        lands in it as ``story-map.md`` rather than in a ``.context`` within the ``.context``."""
        folder_mark = "/" if name.endswith("/") else ""
        declared = PurePosixPath(name)
        if CONTEXT_FOLDER in root.parts and declared.parts[:1] == (CONTEXT_FOLDER,):
            declared = PurePosixPath(*declared.parts[1:])
        return f"{(root / declared).as_posix()}{folder_mark}"
