"""The graph one validate call checks, and the files it is built from."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.tool_call import ToolCall
from harness.guidance.declared_outputs import DeclaredFile
from harness.guidance.guidance import FidelityGuidance
from harness.graph.saved_graph import SavedGraph
from harness.graph.violation import Violation

from cdd_guidance.actions.validate.report_files import ReportFiles

_STORIES = "stories"
# The story map's own node types; the test files a pattern reads into the practice are scoped by the paths named.
_STORY_MAP_TYPES = frozenset({"Epic", "SubEpic", "Story", "Scenario", "Step", "Given", "When", "Then", "Example", "Background"})

if TYPE_CHECKING:
    from space.session.session import Session


@dataclass(frozen=True)
class NamedToCheck:
    """What one validate call names to check: the files being edited (paths), the graph it names (graph: true for the
    session's saved graph, or the graph files), and the call naming them, which says where a graph build runs; none in
    process."""

    paths: list[str] | None = None
    graph: bool | str | list[str] | None = None
    call: ToolCall | None = None


class CheckedGraph:
    """The graph a validate call checks: built from just the files the call names, or from the folders its fidelities
    have written when it names none, and written beside the call's report; or the saved graph or node lists the call
    names. Graph node files are named from the session's root, so every path is kept that way here too.

    It holds the fidelity each listed practice is checked at, which says the format the call checks and where each of
    its formats is written. Validate checks one format of each fidelity, so the declared files of its other formats are
    left out of the report: the formats mirror each other, and judging both reports every finding twice."""

    def __init__(self, session: Session, fidelities: list[FidelityGuidance], to_check: NamedToCheck) -> None:
        self.session = session
        self._call = to_check.call
        self._fidelities = fidelities
        # Read once, so another call changing a fidelity's format mid-way never changes which files this call checks.
        self._formats = [fidelity.format for fidelity in fidelities]
        self._named = to_check.graph
        self.unchecked_files = self._declared_files(in_checked_format=False)
        self.checked_files = self._declared_files(in_checked_format=True)
        # Read now, so a path that is not there is refused before the call claims any report file.
        self._names_paths = bool(to_check.paths)
        self.edited = self._edited_in_checked_format(to_check.paths)
        self.prefixes = self._graph_prefixes()
        self._checked: SavedGraph | None = None
        self.files: list[Path] = []

    def _edited_in_checked_format(self, edited: list[str] | None) -> list[str]:
        """The paths the call names in the checked format, from the session's root."""
        return [path for path in self._from_session_root(edited) if path not in self.unchecked_files]

    def _graph_prefixes(self) -> list[str]:
        """The files the graph is built from: the paths the call names in the checked format; else the folders holding
        what each graph-backed fidelity has written, when the call names no graph, or names the session's graph and
        paths that are all in a format it does not check, since the session's graph is still what it asks to check."""
        if self.edited:
            return self.edited
        builds_written = self._named is None or (self._named is True and self._names_paths)
        return self._from_session_root(self._written_outputs()) if builds_written else []

    def check_beside(self, reports: ReportFiles) -> list[Path]:
        """The graph files this call checks: a graph built from the prefixes and written where reports keeps the call's
        graph, the session's saved graph when the call names true and no file, or the graph files it names."""
        self.files = self._files(reports)
        return self.files

    def violations(self) -> list[Violation]:
        """The listed practices' violations in the graph this call checks that nobody accepted: what the call reports,
        counts, and logs."""
        return self.session.accepted_violations.open_among(self.found())

    def accepted(self) -> list[Violation]:
        """The violations the graph found that a person accepted as they are, which the call leaves out of its report
        and counts there."""
        return self.session.accepted_violations.accepted_among(self.found())

    def found(self) -> list[Violation]:
        """The listed practices' violations in the graph this call checks, accepted or not."""
        keys = [fidelity.practice_guidance.key for fidelity in self._fidelities]
        found = self._checked.violations(keys) if self._checked is not None else []
        if self.prefixes:
            found = [violation for violation in found if violation.is_under(self.prefixes)]
        found = self._on_session_stories(found)
        return self._in_one_format(found)

    def _in_one_format(self, found: list[Violation]) -> list[Violation]:
        """The violations of one format: those in the files of a format the call does not check are dropped only when
        the graph also found some in the checked format's files, so a finding is not reported once for each mirror. A
        graph that reads only the other format, as it reads a model from its markdown while drawio is checked, keeps
        what it found there, which is then no copy of anything."""
        if not any(violation.location in self.checked_files for violation in found):
            return found
        return [violation for violation in found if violation.location not in self.unchecked_files]

    def _on_session_stories(self, found: list[Violation]) -> list[Violation]:
        """The violations inside the work's scope, when the session's ticket names its stories: on those stories and on
        everything held under them (their scenarios, steps, and examples). A violation on any other epic, story,
        scenario, step, or example is another increment's work and is left out; files, and every other practice's
        nodes, are already scoped by the paths the call names."""
        stories = getattr(self.session, "stories", None) or []
        if not stories or self._checked is None:
            return found
        saved = self._checked.practices.get(_STORIES)
        outside = saved.outside(stories, _STORY_MAP_TYPES) if saved is not None else set()
        return [violation for violation in found if violation.node_id not in outside]

    @property
    def unread(self) -> list[str]:
        """The paths the call names that gave the graph it built from them no node of a listed practice, such as a
        sketch or a document no graph reading reads: no graph rule ran on them, so a report with no violation says
        nothing about them. None for a graph the call did not build from paths it names."""
        if not self.edited or self._checked is None or self._named not in (None, True):
            return []
        keys = [fidelity.practice_guidance.key for fidelity in self._fidelities]
        practices = [self._checked.practices[key] for key in keys if key in self._checked.practices]
        files = {node.file.replace("\\", "/") for practice in practices for node in practice.nodes}
        return [path for path in self.edited if not any(file == path or file.startswith(f"{path}/") for file in files)]

    @property
    def held_beside(self) -> list[str]:
        """The folders of the other files the session's graph held when this call checked its files, which a rule over a
        whole practice compared them with; none for a graph this call did not build."""
        return self._checked.held_beside if self._checked is not None else []

    def save_at(self, destination: Path) -> None:
        """Keep the violations of the graph this call checked at destination, beside a report, each with the node it
        was found on, so the board shows the report's violations on their nodes: of the graph it built, the session's
        saved graph, or the graph files it was named. Only those, since the whole graph of a repository runs to a hundred
        megabytes and the board reads none of the rest; a graph file the call was named is left as it is."""
        if destination in self.files or self._checked is None:
            return
        destination.write_text(self._checked.violated.text, encoding="utf-8")

    def found_by(self, fidelity: FidelityGuidance) -> list[Violation]:
        """The violations fidelity's practice found in the graph this call checks, accepted or not: what the session's
        violation history records, so an accepted violation is never recorded as fixed."""
        key = fidelity.practice_guidance.key
        return [violation for violation in self.found() if violation.practice == key]

    def judged_files(self, on_graph: bool) -> str:
        """Each checked format and its files, for the fidelities judged on this call's graph (on_graph) or on their
        files: a model or code fidelity is judged on the graph when the call checks one. The files are the ones the call
        names when it names any, else the ones the fidelity writes in that format."""
        judged = [
            (fidelity, format)
            for fidelity, format in zip(self._fidelities, self._formats)
            if (bool(self.files) and fidelity.is_judged_on_graph) == on_graph
        ]
        return "; ".join(f"{format}: {', '.join(self.edited or fidelity.session_output.written.output_paths().get(format, []))}" for fidelity, format in judged)

    def _files(self, reports: ReportFiles) -> list[Path]:
        if self.prefixes and self._named in (None, True) and self._fidelities:
            return [self._built_at(reports.graph_file())]
        if self._named is True:
            return self._session_saved() or self._built_from_written(reports)
        return self._read_named()

    def _built_from_written(self, reports: ReportFiles) -> list[Path]:
        """The session's graph when none is saved yet, "created for the session and loaded when it is missing": built
        from what each listed fidelity has written, so a call naming the session's graph checks it instead of nothing."""
        self.prefixes = self._from_session_root(self._written_outputs())
        if not (self.prefixes and self._fidelities):
            return []
        return [self._built_at(reports.graph_file())]

    def _session_saved(self) -> list[Path]:
        """The session's saved graph, read from the file its graph saves in; none when nothing is saved there."""
        saved_file = self.session.graph.saved_file
        self._checked = saved_file.read()
        return [saved_file.path] if self._checked is not None else []

    def _read_named(self) -> list[Path]:
        """The graph files the call names, one path or several, each read as the graph it holds: one file is checked as
        its graph, and several as one graph of all their violations. None for nothing. Each is named from the project's
        root, or absolute, and one that is not there is refused by name."""
        named = self._named
        entries = [named] if isinstance(named, str) else list(named or [])
        files = [self.session.session_files.existing(str(entry).strip()) for entry in entries if str(entry).strip()]
        graphs = [SavedGraph.from_file(file) for file in files]
        if len(graphs) == 1:
            self._checked = graphs[0]
        elif graphs:
            self._checked = SavedGraph.from_violations([violation for graph in graphs for violation in graph.violations()])
        return files

    def _built_at(self, destination: Path) -> Path:
        """Refresh the session's graph with the edited files, read as they are now, keep the nodes read from them as this
        call's graph, written at destination for the report; the saved graph stays as it is. The refresh and the nodes
        it keeps are one change to the graph (``graph.refreshed``), so another call's refresh never comes between them,
        and each call writes its own file, so calls running at once never read each other's report graph. For a chat's
        call the graph's worker writes the file, so the server answering chats never serialises the nodes; this call
        reads back only the nodes of the files it names.

        The session's graph holds every practice, because one builds on another (DDD building blocks come from the
        clean engineering classes); the report keeps only the listed guidance's practice."""
        self.session.graph.reads.hold_whole(self._call)
        self.session.graph.reads.refreshed(self.prefixes, destination, self._call)
        self._checked = SavedGraph.from_file(destination)
        return destination

    def _from_session_root(self, paths: list[str] | None) -> list[str]:
        """Each named path as graph node files record it, relative to the session's root.

        A relative path is read from the project's checkout, where the agent works and every path it sees starts. The
        session's files refuse a path that is not there, or not under the session's root: the graph would be built
        from nothing, and its empty report would read as a clean validate."""
        return [self.session.session_files.from_root(item) for item in paths or []]

    def _declared_files(self, in_checked_format: bool) -> set[str]:
        """The declared files of the format validate checks (in_checked_format), or of every format it does not check,
        as graph node files record them. A declared path that names no one file is left out."""
        declared = [
            self.session.paths.path_named(path)
            for fidelity, checked in zip(self._fidelities, self._formats)
            for format, paths in fidelity.session_output.written.output_paths().items()
            if (format == checked) == in_checked_format
            for path in paths
            if DeclaredFile(path).names_one_path
        ]
        return {self.session.session_files.from_root(path) for path in declared if path.exists() and self.session.session_files.in_root(path)}

    def _written_outputs(self) -> list[str]:
        """The folders holding what each listed fidelity declares in its checked format and has already written. The
        folder, not the file, because a story map's stories keep their scenarios in files beside it."""
        declared = [path for fidelity, checked in zip(self._fidelities, self._formats) for path in fidelity.session_output.written.output_paths().get(checked, [])]
        found = [path for named in declared for path in self._written_at(named)]
        folders = {path.parent if path.is_file() else path for path in found if path.exists()}
        return sorted(str(folder) for folder in folders if self.session.session_files.in_root(folder))

    def _written_at(self, declared: str) -> list[Path]:
        """Where a declared path is written: the path itself, or, for one with a named part, such as ``src/{module}/``,
        each folder that part can name, which are the folders in the folder above it. A folder whose name opens with a
        dot holds no written output, such as ``.git`` or ``.sessions``."""
        above, named_part, _ = declared.partition("{")
        if not named_part:
            return [self.session.paths.path_named(declared)]
        path = self.session.paths.path_named(above)
        if not above.endswith("/"):
            # The named part is in a file's name, so the files are in the folder itself.
            return [path.parent]
        if not path.is_dir():
            return []
        return [folder for folder in sorted(path.iterdir()) if folder.is_dir() and not folder.name.startswith(".")]
