"""What each practice and each of its fidelities has in one session: where it writes and the files it declares."""

from __future__ import annotations

import os
from functools import cache
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Callable, Iterable

from cdd_guidance.practices.source_code import is_test_code
from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.design_canvas.versions import CanvasVersions
from harness.guidance.declared_outputs import DeclaredFile
from harness.installation.data_class import data_field, identity, language_adapter
from harness.mcp.mcp_annotations import mcp
from harness.whiteboard import BoardLinks, Whiteboard
from cdd_guidance.practices.stories.model.story_map_files import STORY_TESTS_FOLDER
from harness.installation.context_config import CONTEXT_FOLDER, DEFAULT_FORMAT
from harness.markdown.format import Format
from space.session.answer_reads import HeldForAnswer
from space.session.file_manager import FileEntry
from space.session.proposed_roots import ProposedRoots, code_extensions
from space.session.validation_report import ValidationReports

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, GuidanceCollection, PracticeGuidance
    from space.session.session import Session
    from space.session.session_record import FidelityFields, PracticeFields

_OUTPUT_PATTERN_MARKS = {"*", "{"}


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
        # What each fidelity has in this session, held once it is first asked for.
        self._fidelity_outputs: dict[FidelityGuidance, FidelitySessionOutput] = {}

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
        """What fidelity, one of this practice's, has in this session: made the first time it is asked for, then held,
        so each fidelity has one output in the session."""
        held = self._fidelity_outputs.get(fidelity)
        if held is None:
            held = self._fidelity_outputs[fidelity] = FidelitySessionOutput(self, fidelity)
        return held

    @property
    def fidelity_outputs(self) -> list[FidelitySessionOutput]:
        """What each of the practice's fidelities has in this session, each held once."""
        return [self.of_fidelity(fidelity) for fidelity in self.fidelities]

    def holds(self, file: Path) -> bool:
        """Whether file is one of the files a fidelity of this practice writes in this session."""
        return any(output.written.holds(file) for output in self.fidelity_outputs)

    @property
    def fidelities(self) -> GuidanceCollection:
        """The practice's fidelities, such as story_map, by name, each able to list its files in this session."""
        return self._guidance.fidelities

    @property
    def fields(self) -> PracticeFields:
        """What session.json keeps for this practice: whether it is on, the root a person chose, and what each of its
        fidelities keeps, which each fidelity's FidelitySessionOutput reads and saves for itself."""
        return self._session.record.fields.practice(self.name)

    def change(self, change: Callable[[PracticeFields], object], said: str) -> None:
        """Change what session.json keeps for this practice, as the file holds it now; said names the change."""
        self._session.record.update(lambda fields: change(fields.practice(self.name)), f"{self.name} {said}")

    @property
    @data_field
    def short_name(self) -> str:
        """The practice's short name, such as DDD, which a toggle for it shows."""
        return self._guidance.short_name

    @property
    @data_field
    def colour(self) -> str:
        """The practice's colour, which its toggles and fidelity dots are drawn in."""
        return self._guidance.colour

    @property
    @data_field
    def fidelity_slugs(self) -> list[str]:
        """The slugs of this practice's fidelities, such as stories-story-map, so a page listing a stage's files knows
        which of them this practice owns and hides them while it is off."""
        return [fidelity.slug for fidelity in self.fidelities]

    @property
    @data_field
    def enabled(self) -> bool:
        """Whether the session works on this practice: true until a person turns it off."""
        return self.fields.enabled

    @mcp
    @agent_tool
    @noSessionLog
    def enable(self, is_enabled: bool) -> PracticeSessionOutput:
        """Turn this practice on or off for its session, saved in its session.json; its guidance selection changes."""
        self.change(lambda fields: setattr(fields, "enabled", is_enabled), f"enabled {is_enabled}")
        self._session.guidance.changed()
        return self

    @property
    def _chosen_or_configured_root(self) -> str | None:
        """Where this practice writes, relative to the session's root, when someone said: the root a person chose in
        this session, else the folder the project's ``.context/config.json`` names for the practice."""
        return self.fields.root or self._configured_folder.get(
            self._session.answer, lambda: self._session.context_config.practice_folder(self.name)
        )

    @property
    def folder(self) -> Path:
        """The folder this practice writes its code under: the root chosen or configured,
        else the practice's own default folder under the session's root, such as src for BDD."""
        relative = self._chosen_or_configured_root or self._guidance.default_workspace_folder
        return self._session.paths.folder_under_root(relative)

    @property
    def output_root(self) -> Path:
        """The folder this practice's fidelities declare their outputs under: the root chosen or configured, else the
        session's root itself. A declared output such as `.context/story-map.md` or `**/*_spec.py` is named from the
        workpath, so the practice's own default folder is not added."""
        return self._session.paths.folder_under_root(self._chosen_or_configured_root or ".")

    @property
    def output_folders(self) -> set[Path]:
        """Every folder this practice's fidelities write their declared outputs in, up to the first part a name or a
        pattern fills in, such as ``story_tests`` for ``story_tests/{epic}/{sub-epic}/...``: a viewer of the session's
        files reads each of them."""
        paths = (path for fidelity in self.fidelities.entries.values() for paths in fidelity.session_output.written.output_paths().values() for path in paths)
        return {self._fixed_folder(path) for path in paths}

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
        return self._session.paths.from_project(self.folder)

    @property
    @data_field
    def is_root_chosen(self) -> bool:
        """Whether a person chose this practice's root, rather than it being the default."""
        return bool(self.fields.root)

    @property
    def is_root_default(self) -> bool:
        """Whether nobody said where this practice writes: no root chosen in the session, none configured for the
        project, so it writes under its own default folder."""
        return not self._chosen_or_configured_root

    @mcp
    @agent_tool
    @noSessionLog
    def choose_root(self, path: str) -> PracticeSessionOutput:
        """Write this practice's files under path, a folder in the repository. An empty path and a file are refused."""
        self.keep_root(self.root_named(path))
        return self

    def root_named(self, path: str) -> Path:
        """The folder path names as a root, read from the repository; an empty path, which names no folder, and a path
        to a file raise *OutputRootRefused*. A folder that is not there yet is a root the practice writes into."""
        if not str(path or "").strip():
            raise OutputRootRefused(path, "an empty path names no folder")
        root = self._session.checkout.root / path
        if root.is_file():
            raise OutputRootRefused(path, f"{path} is a file")
        return root

    def keep_root(self, root: Path) -> None:
        """Write this practice's files under root, kept in session.json relative to the workpath, so the root still
        names the same folder after the workpath moves."""
        relative = Path(os.path.relpath(Path(root).resolve(), self._session.work_root)).as_posix()
        self.change(lambda fields: setattr(fields, "root", relative), f"root {relative}")

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_root(self) -> PracticeSessionOutput:
        """Write this practice's files under its default root again: the workpath plus the practice's own folder."""
        self.change(lambda fields: setattr(fields, "root", ""), "root default")
        return self

    def _fixed_folder(self, path: str) -> Path:
        """The folder of path up to its first part a name or pattern fills in; a file's own folder when none does."""
        parts = Path(path).parts
        filled = next((index for index, part in enumerate(parts) if set(part) & set("{*?")), None)
        if filled is not None:
            return Path(*parts[:filled])
        return Path(path) if path.endswith("/") else Path(path).parent


class OutputRootRefused(ValueError):
    """A path was chosen as the root a practice or a fidelity writes under that names no folder: an empty path, or a
    file. Kept as a root, the agent would be told to write its files there."""

    def __init__(self, path: str, reason: str) -> None:
        super().__init__(f"{reason}; choose a folder in the repository as a root")
        self.path = path


class FormatNotOfferedError(ValueError):
    """A format was chosen for a fidelity that does not write it."""

    def __init__(self, fidelity: FidelityGuidance, format: str) -> None:
        super().__init__(f"{fidelity.name} does not write {format}; it writes {', '.join(fidelity.session_output.offered_formats) or 'nothing'}")
        self.fidelity = fidelity
        self.format = format


class FidelityNotInPractice(LookupError):
    """A fidelity was named that the practice does not have, by its name or its slug."""

    def __init__(self, practice: PracticeGuidance, fidelity: str) -> None:
        names = ", ".join(item.name for item in practice.fidelities)
        super().__init__(f"{practice.slug} has no fidelity named {fidelity}; it has {names}")
        self.practice = practice
        self.fidelity = fidelity


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
        # The formats it uses from each group of the formats it writes, and its validation reports in the session.
        self.formats = FidelityFormats(self)
        self.validation_reports = ValidationReports(self)
        # The files it writes in the session: where each format goes, which are there, and which the branch changed.
        self.written = WrittenFiles(self)
        # The folders it proposes for the pieces the session's ticket works on, before a person confirms them as roots.
        self.proposed_roots = ProposedRoots(self)

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str, fidelity: str, *, call: ToolCall) -> FidelitySessionOutput:
        """The fidelity fidelity names, by its name (story_map, story-map) or its slug (stories-story-map), of the
        practice named practice in the session whose session.json is session, a path from the project the call names."""
        guidance = call.session_named(session).practice(practice).guidance
        found = guidance.fidelities.called(fidelity) or guidance.answers_to(fidelity)
        # The practice's own slug answers the practice, which is not one of its fidelities.
        if found is None or found is guidance:
            raise FidelityNotInPractice(guidance, fidelity)
        return found.session_output

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
        """The formats this fidelity writes, in the order its practice declares them: what a person can choose. An output
        named for what it holds, such as thin_slice, is files the fidelity writes, not a format, so it is not offered."""
        return [name for name in self._fidelity.outputs if Format(name).is_offered]

    @property
    @data_field
    def chosen_formats(self) -> list[str]:
        """The formats chosen for this fidelity in the session, in the order chosen: what a story map edit renders to
        and what a chip shows picked. Until a person or an action chooses, the project's defaults for it, else its
        default format."""
        chosen = self.fields.formats
        return self.formats.default_formats if chosen is None else chosen

    @mcp
    @agent_tool
    @noSessionLog
    def choose_root(self, path: str) -> FidelitySessionOutput:
        """Write this fidelity's files under path, a folder in the repository, apart from its practice's root; an empty path and a file are refused: such as the stories scenarios and acceptance tests of one epic in story_tests/<epic>, while the story map stays in the practice's root, the project's .context."""
        self.keep_roots([self._practice.root_named(path)])
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def add_root(self, path: str) -> FidelitySessionOutput:
        """Write this fidelity's files under path as well, a folder in the repository, beside the roots it has; an empty path and a file are refused: such as one more sub-epic's folder in story_tests that the session's ticket works on, so the session holds that sub-epic's scenarios and story tests and no other's."""
        self.keep_roots([*self.roots, self._practice.root_named(path)])
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def propose_roots(self, names: list[str]) -> list[str]:
        """Return the folders this fidelity proposes to write under, each a path from the project as choose_root and add_root take it: the narrowest folder holding each piece the session's branch changed, and each piece names name, such as the aggregate or the story a ticket's text names (an aggregate's folder, a package, a sub-epic's folder in story_tests). Show them to the person and set only those confirmed."""
        return self.proposed_roots.proposed(names)

    @mcp
    @agent_tool
    @noSessionLog
    def choose_format(self, format: str, is_chosen: bool) -> FidelitySessionOutput:
        """Choose format for this fidelity in its session, or leave it out when is_chosen is false, saved in its
        session.json. A format the fidelity does not write is refused."""
        named = Format(format).name
        if named not in self.offered_formats:
            raise FormatNotOfferedError(self._fidelity, format)
        others = [each for each in self.chosen_formats if each != named]
        chosen = self.chosen_formats if is_chosen and named in self.chosen_formats else others + ([named] if is_chosen else [])
        self._change(lambda fields: setattr(fields, "formats", chosen), f"formats {', '.join(chosen)}")
        self._session.guidance.changed()
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

    @property
    def fields(self) -> FidelityFields:
        """What session.json keeps for this fidelity: the formats chosen, its own roots, and a file name per format for
        a single-file output."""
        return self._practice.fields.fidelity(self._fidelity.name)

    def _change(self, change: Callable[[FidelityFields], object], said: str) -> None:
        self._practice.change(lambda fields: change(fields.fidelity(self._fidelity.name)), f"{self._fidelity.name} {said}")

    def keep_roots(self, roots: list[Path]) -> None:
        """Write this fidelity's files under each of roots, such as the folders of the sub-epics a ticket works on in
        story_tests, apart from its practice's root; kept in session.json relative to the workpath, in place of every
        root it had."""
        relative = list(dict.fromkeys(Path(os.path.relpath(Path(root).resolve(), self._session.work_root)).as_posix() for root in roots))
        self._change(lambda fields: setattr(fields, "roots", relative), f"roots {', '.join(relative)}")

    @property
    def root(self) -> Path:
        """The first folder this fidelity writes under (``roots``)."""
        return self.roots[0]

    @property
    def roots(self) -> list[Path]:
        """The folders this fidelity writes under: its own roots when session.json names them, as ``roots`` or one
        ``root``, else its practice's output root."""
        named = self.fields.roots
        return [self._session.paths.folder_under_root(root) for root in named] or [self._practice.output_root]


class WrittenFiles:
    """The files one fidelity writes in a session: where it writes each format under its root, the files it declares
    there, whether any is there yet, and which the session's branch changed, so a page can show only those."""

    def __init__(self, output: FidelitySessionOutput) -> None:
        self._output = output

    @property
    def _fidelity(self) -> FidelityGuidance:
        return self._output.fidelity

    @property
    def _session(self) -> Session:
        return self._output.practice.session

    def output_paths(self) -> dict[str, list[str]]:
        """Where this fidelity writes each format in the session: its declared paths under its root. session.json can
        name a file per format for a single-file output."""
        chosen, roots = self._output.fields.file_names, self._output.roots
        return {
            label: list(dict.fromkeys(path for root in roots for name in self._output_names(declared, chosen.get(label)) if (path := self._under_root(name, root))))
            for label, declared in self._fidelity.outputs.items()
        }

    def _listed_paths(self) -> dict[str, list[str]]:
        """The declared paths a page lists files by. A code format written as a folder for each module is listed by its
        folders alone, as the code the session worked on: the file it declares in that folder, such as
        ``{module}/{module}.py``, says where a render writes and is one of those files once the session changes it, so
        it is not searched for across every module."""
        folders = self._fidelity.declared.code_folders()
        return {label: [path for path in paths if path.endswith("/")] if label in folders else paths for label, paths in self.output_paths().items()}

    def files(self) -> dict[str, list[FileEntry]]:
        """The files this fidelity declares in the session, by format, each with its path from the project, whether it
        exists, and whether the session's branch changed it, so a page can show only the changed ones."""
        # Asking git what the branch changed is slow, so it is asked only once a file is there.
        changed = cache(self._session.session_files.branch_changes.files)
        output_paths = self._listed_paths()
        found = self._found_by_pattern(self._listed(path) for paths in output_paths.values() for path in paths)
        return {
            label: [entry for path in paths for entry in self._declared_files(label, path, changed, found)]
            for label, paths in output_paths.items()
        }

    def _found_by_pattern(self, declared: Iterable[DeclaredFile]) -> dict[str, list[Path]]:
        """The files each pattern among declared finds in the session's checkout, by its glob, all searched in one go; a
        path that names one file is looked at where it is, not searched for."""
        return self._session.session_files.find_each(file.glob for file in declared if not file.names_one_path)

    def holds(self, file: Path) -> bool:
        """Whether file, in the session's checkout, is one of this fidelity's, changed by the session or not: the
        session's sketch, a file one of its outputs names, or production code under a folder it writes code to, and either way one its practice
        claims, since a pattern such as DDD's ``{bounded_context}/{aggregate}/{aggregate}.py`` fits files of no domain.
        A page lists every file of the fidelities it shows. The session's sketch is every fidelity's, since it holds a
        section for each practice."""
        if self._session.paths.is_sketch(file):
            return True
        if not (self._fidelity.declared.includes(self._session.repo.path_from_top(file)) or self._writes_code_to(file)):
            return False
        practice = self._fidelity.practice_guidance
        return practice is None or practice.claims(file)

    def _writes_code_to(self, file: Path) -> bool:
        """Whether file is production code in a format this fidelity writes as a folder per module, under its root."""
        roots = [root.resolve() for root in self._output.roots]
        if not any(root in file.resolve().parents for root in roots) or is_test_code(file.as_posix()):
            return False
        return any(file.suffix in code_extensions(label) for label in self._fidelity.declared.code_folders())

    def every_file(self) -> list[Path]:
        """Every file this fidelity declares that is in the session's checkout, worked on by the session or not: what a
        reader links to, such as each acceptance test of a story."""
        repo = self._session.repo
        listed = [(label, self._listed(path)) for label, paths in self._listed_paths().items() for path in paths]
        searched = self._found_by_pattern(declared for _label, declared in listed)
        found: list[Path] = []
        for label, declared in listed:
            named = [repo.root / declared.glob] if declared.names_one_path else self._found(label, declared, searched)
            found += [file for file in named if file.is_file()]
        return found

    def saved_beside(self, source: Path, format: str) -> Path | None:
        """Where a render of the file at source into format is saved in the session: the file the fidelity's declared
        outputs place for it (``DeclaredOutputs.file_beside``), under the root of this fidelity that holds source. None
        when source is under none of its roots, or no file is placed for it."""
        resolved = source.resolve()
        for root in (root.resolve() for root in self._output.roots):
            if root in resolved.parents:
                placed = self._fidelity.declared.file_beside(resolved.relative_to(root).as_posix(), format)
                return root / placed if placed else None
        return None

    def files_to_review(self) -> dict[str, list[FileEntry]]:
        """The files a person reviews for the fidelity, by format: its own, or those of the fidelities of its practice it
        reviews files of, in the order it names them, each file once."""
        names = self._fidelity.reviews_files_of
        if not names:
            return self.files()
        practice = self._output.practice
        reviewed: dict[str, list[FileEntry]] = {}
        for name in names:
            fidelity = practice.fidelities.entries.get(name)
            for label, entries in (practice.of_fidelity(fidelity).written.files() if fidelity is not None else {}).items():
                known = {entry.path for entry in reviewed.get(label, [])}
                reviewed.setdefault(label, []).extend(entry for entry in entries if entry.path not in known)
        return reviewed

    def has_output(self) -> bool:
        """Whether a file this fidelity declares is already in the session, such as one a person wrote. Unlike
        ``files`` it never asks git, and the board asks this of every fidelity."""
        return self.has_named_output() or self.has_found_output()

    def has_named_output(self) -> bool:
        """Whether a file this fidelity names by its whole path is there: one look each, quick enough for every read."""
        return any(self._exists(file) for _label, file in self._declared_outputs() if file.names_one_path)

    def has_found_output(self) -> bool:
        """Whether a pattern this fidelity declares finds a file, which searches the session's folders: slow enough that
        the board keeps the answer. A pattern counts only in a session with a folder of its own, since on the whole
        repository a pattern also finds other sessions' files."""
        if self._session.work_root == self._session.repo.root:
            return False
        patterns = [(label, file) for label, file in self._declared_outputs() if not file.names_one_path]
        searched = self._found_by_pattern(file for _label, file in patterns)
        return any(self._found(label, file, searched) for label, file in patterns)

    def _declared_outputs(self) -> list[tuple[str, DeclaredFile]]:
        return [(label, self._declared(path)) for label, paths in self._listed_paths().items() for path in paths]

    def _declared(self, path: str) -> DeclaredFile:
        """A declared path under this fidelity's root, as a path from the project."""
        return DeclaredFile(self._session.repo.path_from_top(path))

    def _listed(self, path: str) -> DeclaredFile:
        """A declared path as a page lists it. A session on the whole repository, such as main, holds every module's
        documents, so where this fidelity writes at the repository's own folder, a path in ``.context`` is searched for
        in every ``.context`` folder and the folders inside it, such as ``harness/.context/stories/story-map.md``, as
        its patterns already find its tests anywhere."""
        from_top = PurePosixPath(self._session.repo.path_from_top(path))
        if all(root.resolve() != self._session.repo.root.resolve() for root in self._output.roots) or from_top.parts[:1] != (CONTEXT_FOLDER,):
            return DeclaredFile(from_top.as_posix())
        return DeclaredFile(PurePosixPath("**", CONTEXT_FOLDER, "**", *from_top.parts[1:]).as_posix())

    def _declared_files(self, label: str, path: str, changed: Callable[[], set[Path]], searched: dict[str, list[Path]]) -> list[FileEntry]:
        """A declared path, or each file the fidelity declares where a pattern searches (searched holds what each
        pattern found), each marked when the session's branch changed it; a pattern that finds none lists nothing, a
        pattern being no file. A path widened to every ``.context`` folder that finds none lists the declared path
        itself, so a page still shows where it goes."""
        repo = self._session.repo
        if path.endswith("/") and Format(label).is_code:
            return self._worked_on_code(label, changed)
        listed, declared = self._listed(path), self._declared(path)
        found = [] if listed.names_one_path else self._found(label, listed, searched)
        if found:
            return [FileEntry(repo.path_from_top(file), True, file.resolve() in changed()).linked(published_link(file)) for file in found]
        if declared.names_one_path:
            named = latest_version(repo.root / declared.glob)
            path = repo.path_from_top(named) if named.exists() else declared.glob
            return [FileEntry(path, named.exists(), named.exists() and named.resolve() in changed()).linked(published_link(named))]
        return []

    def _worked_on_code(self, label: str, changed: Callable[[], set[Path]]) -> list[FileEntry]:
        """The code a fidelity that declares a folder per module writes, such as Clean Engineering's ``{module}/``: the
        files in that format under its root that the session's branch changed, the code the ticket worked on, not every
        file of that language in the repository. Specs, tests, and what only they use are the acceptance tests' and the
        development specs' files, not production code, so they are left out."""
        roots = [root.resolve() for root in self._output.roots]
        extensions = code_extensions(label)
        worked_on = sorted(
            file for file in changed() if file.suffix in extensions and any(file == root or root in file.parents for root in roots) and not is_test_code(file.as_posix())
        )
        return [FileEntry(self._session.repo.path_from_top(file), file.exists(), True) for file in worked_on]

    def _found(self, label: str, declared: DeclaredFile, searched: dict[str, list[Path]]) -> list[Path]:
        """The files a declared pattern's search found (searched, by glob) that it declares: a name used twice in one
        declared path must be the same text both times."""
        return [file for file in searched[declared.glob] if self._fidelity.declared.includes(file.as_posix(), label) or declared.pattern.search(file.as_posix())]

    def _exists(self, declared: DeclaredFile) -> bool:
        """Whether the file the declared path names outright is in the repository."""
        return (self._session.repo.root / declared.glob).exists()

    def _output_names(self, declared: str | list[str], chosen_name: str | None) -> list[str]:
        """The file names a declared output writes: the chosen name in place of the declared one for a single-file
        output."""
        names = [declared] if isinstance(declared, str) else list(declared)
        is_single_file = len(names) == 1 and not set(names[0]) & _OUTPUT_PATTERN_MARKS
        return [PurePosixPath(names[0]).with_name(chosen_name).as_posix()] if chosen_name and is_single_file else names

    def _under_root(self, name: str, root: Path) -> str:
        """A declared name under root, this fidelity's root. A root inside a ``.context`` folder, such as
        ``harness/.context/stories``, holds the practice's documents itself, so a declared ``.context/story-map.md``
        lands in it as ``story-map.md`` rather than in a ``.context`` within the ``.context``; a declared
        ``story_tests/...`` lands in the ``story_tests`` beside that ``.context``, or, for a root inside ``story_tests``
        such as one epic's folder, under that root; empty when the root names a folder deeper than the declared path
        goes."""
        folder_mark = "/" if name.endswith("/") else ""
        declared = PurePosixPath(name)
        if STORY_TESTS_FOLDER in root.parts and declared.parts[:1] == (STORY_TESTS_FOLDER,):
            below = self._below_named(declared, root)
            # An epic's own stories' file is not below a sub-epic's folder: the root already names more folders than it does.
            return f"{(root / below).as_posix()}{folder_mark}" if below.parts else ""
        if CONTEXT_FOLDER in root.parts and declared.parts[:1] == (STORY_TESTS_FOLDER,):
            return f"{(self._beside_context(root) / declared).as_posix()}{folder_mark}"
        if CONTEXT_FOLDER in root.parts and declared.parts[:1] == (CONTEXT_FOLDER,):
            declared = PurePosixPath(*declared.parts[1:])
        return f"{(root / declared).as_posix()}{folder_mark}"

    def _below_named(self, declared: PurePosixPath, root: Path) -> PurePosixPath:
        """The part of a declared ``story_tests/{epic}/{sub-epic}/...`` path below a root inside ``story_tests``, such as
        a session's epic folder: the folders the root already names, ``story_tests`` and one name per folder below it,
        are dropped."""
        named = len(root.parts) - root.parts.index(STORY_TESTS_FOLDER)
        return PurePosixPath(*declared.parts[named:])

    def _beside_context(self, root: Path) -> Path:
        """The folder holding the `.context` root sits in, where a project keeps its `story_tests` beside its
        `.context`."""
        return Path(*root.parts[: root.parts.index(CONTEXT_FOLDER)])


def latest_version(file: Path) -> Path:
    """The latest version of file kept beside it, ``story-map.version-2.whiteboard`` for ``story-map.whiteboard``: a
    board regenerated after people edited it is published as a new version, so a page opens the newest; file itself
    when no version is kept."""
    numbered = {}
    for sibling in file.parent.glob(f"{file.stem}.version-*{file.suffix}") if file.parent.is_dir() else []:
        number = sibling.name[len(file.stem) + len(".version-"): -len(file.suffix) or None]
        if number.isdigit():
            numbered[int(number)] = sibling
    return numbered[max(numbered)] if numbered else file


def published_link(file: Path) -> str:
    """The link a file is published at, which a page opens instead of the file: a design canvas version's
    ``canvas.json`` (``<design-canvas>/version-N/project/canvas.json``) at the link its versions record
    (``versions.json``), and a ``.whiteboard`` file at the address of the board in Claude kept beside it
    (``whiteboards.json``); none for any other file, or one not yet published."""
    if file.suffix == Whiteboard.SUFFIX:
        return BoardLinks.beside(file).of(file)
    if file.name != "canvas.json" or file.parent.name != "project":
        return ""
    version = file.parent.parent
    return CanvasVersions(version.parent).published.of(version.name) or ""


class FidelityFormats:
    """The formats one fidelity uses from each group of the formats it writes in a session, such as its diagram formats:
    those chosen there, else those choosing the group would choose."""

    def __init__(self, output: FidelitySessionOutput) -> None:
        self._output = output

    @property
    def _fidelity(self) -> FidelityGuidance:
        return self._output.fidelity

    def used_from(self, group: list[str]) -> list[str]:
        """The formats this fidelity uses from a group of the formats it writes, such as its diagram formats: those
        chosen there, else those it would choose. A chip standing for the group does each of them."""
        return self.chosen_from(group) or self.wanted_from(group)

    def chosen_from(self, group: list[str]) -> list[str]:
        """The formats chosen for this fidelity from group, in the order chosen."""
        return [name for name in self._output.chosen_formats if name in group]

    def is_chosen_from(self, group: list[str]) -> bool:
        """Whether group is chosen for this fidelity: every format of a diagram it writes, the draw.io file and the
        Claude Whiteboard board, else any format of the group."""
        chosen = self.chosen_from(group)
        if group and Format(group[0]).is_written_with_its_group:
            return all(name in chosen for name in group)
        return bool(chosen)

    def wanted_from(self, group: list[str]) -> list[str]:
        """What choosing group chooses: every format of a diagram this fidelity writes; for any other group the
        project's default formats for this fidelity in it, else its default format when group holds it, else group's
        first."""
        if group and Format(group[0]).is_written_with_its_group:
            return list(group)
        defaults = [name for name in self.default_formats if name in group]
        own = self._fidelity.default_format.name if self._fidelity.default_format else ""
        return defaults or [own if own in group else group[0]]

    def choose_from(self, group: list[str], is_chosen: bool) -> None:
        """Choose every format this fidelity would use from group, or leave out every one of group chosen for it."""
        for name in (self.wanted_from(group) if is_chosen else self.chosen_from(group)):
            self._output.choose_format(name, is_chosen)

    @property
    def default_formats(self) -> list[str]:
        """The formats the project's ``.context/config.json`` chooses for this fidelity by default, ``default`` standing
        for the fidelity's own default format, each the fidelity writes and each once; its own default format when the
        project names none, or none it writes."""
        own = [self._fidelity.default_format.name] if self._fidelity.default_format else []
        configured = self._output.practice.session.context_config.default_formats(self._output.practice.name, self._fidelity.name)
        if configured is None:
            return own
        named = [name for each in configured for name in (own if each == DEFAULT_FORMAT else [Format(each).name])]
        offered = [name for name in dict.fromkeys(named) if name in self._output.offered_formats]
        return offered or own

