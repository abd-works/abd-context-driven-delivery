"""The graph one validate call checks, and the files it is built from."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.tool_call import ToolCall
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.graph.saved_graph import SavedGraph
from harness.graph.violation import Violation

from cdd_guidance.actions.validate.checked_fidelity import CheckedFidelity
from cdd_guidance.actions.validate.report_files import ReportFiles


if TYPE_CHECKING:
    from space.session.session import Session


@dataclass(frozen=True)
class NamedToCheck:
    """What one validate call names to check: the files being edited (paths), the graph it names (graph: true for the
    session's saved graph, or the graph files), the call naming them, which says where a graph build runs, none in
    process; and whether it asks for the judged pass (judge_all), which lists the candidates of the judged rules that
    run over the whole working copy."""

    paths: list[str] | None = None
    graph: bool | str | list[str] | None = None
    call: ToolCall | None = None
    judge_all: bool = False


class CheckedGraph:
    """The graph a validate call checks: built from just the files the call names, or from the folders its fidelities
    have written when it names none, and written beside the call's reports; or the saved graph or node lists the call
    names. Graph node files are named from the session's root, so every path is kept that way here too.

    It holds each fidelity the call checks (its *CheckedFidelity*), which says the format the call checks and where each
    of its formats is written, and the report files it claims for them, which it saves the call's report into."""

    def __init__(self, session: Session, checked: list[CheckedFidelity], to_check: NamedToCheck) -> None:
        self._session = session
        self._call = to_check.call
        self._checked_fidelities = list(checked)
        self._named = to_check.graph
        self._judge_all = to_check.judge_all
        # Read now, so a path that is not there is refused before the call claims any report file.
        self._names_paths = bool(to_check.paths)
        self._edited = self._edited_in_checked_format(to_check.paths)
        self._built_from = self._graph_prefixes()
        self._reports = ReportFiles(session, self._checked_fidelities)
        self._checked: SavedGraph | None = None
        self._files: list[Path] = self._graph_files()

    @property
    def session(self) -> Session:
        return self._session

    @property
    def edited(self) -> list[str]:
        """The paths the call names in the checked format, from the session's root."""
        return list(self._edited)

    @property
    def files_built_from(self) -> list[str]:
        """The files and folders the graph is built from, from the session's root; none for a graph the call names."""
        return list(self._built_from)

    @property
    def files(self) -> list[Path]:
        """The graph files this call checks: a graph built from the files it was built from and written where its
        reports keep the call's graph, the session's saved graph when the call names true and no file, or the graph
        files it names."""
        return list(self._files)

    @property
    def reports(self) -> ReportFiles:
        return self._reports

    def save(self, text: str) -> None:
        """Save text, the call's report, into each claimed report file, with the violations of the graph this call
        checked kept beside each under the same name, and record each in the session's violation history: the hits its
        fidelity's practice found in the files the call checked, accepted or not."""
        self._reports.save(text)
        history = self._session.folder.violation_history
        for checked in self._checked_fidelities:
            self.save_at(checked.report.saved_graph)
            history.record(checked.report, self.found_by(checked.fidelity), self._built_from)

    @property
    def _checked_files(self) -> set[str]:
        return {file for checked in self._checked_fidelities for file in checked.checked_files}

    @property
    def _other_format_files(self) -> set[str]:
        return {file for checked in self._checked_fidelities for file in checked.other_format_files}

    def _edited_in_checked_format(self, edited: list[str] | None) -> list[str]:
        """The paths the call names in the checked format, from the session's root."""
        other_formats = self._other_format_files
        return [path for path in self._from_session_root(edited) if path not in other_formats]

    def _graph_prefixes(self) -> list[str]:
        """The files the graph is built from: the paths the call names in the checked format; else the folders holding
        what each graph-backed fidelity has written, when the call names no graph, or names the session's graph and
        paths that are all in a format it does not check, since the session's graph is still what it asks to check."""
        if self._edited:
            return self._edited
        builds_written = self._named is None or (self._named is True and self._names_paths)
        return self._from_session_root(self._written_outputs()) if builds_written else []

    def violations(self) -> list[Violation]:
        """The listed practices' violations in the graph this call checks that nobody accepted: what the call reports,
        counts, and logs."""
        return self._session.accepted_violations.open_among(self.found())

    def accepted(self) -> list[Violation]:
        """The violations the graph found that a person accepted as they are, which the call leaves out of its report
        and counts there."""
        return self._session.accepted_violations.accepted_among(self.found())

    def found(self) -> list[Violation]:
        """The listed practices' violations in the graph this call checks, accepted or not: those in the files it was
        built from, and, of a rule that runs over the whole working copy, those anywhere, its candidates only when the
        call asks for the judged pass."""
        keys = [checked.fidelity.practice_guidance.key for checked in self._checked_fidelities]
        found = self._checked.violations(keys) if self._checked is not None else []
        found = [violation for violation in found if violation.is_reported_for(self._built_from, self._judge_all)]
        found = self._on_session_stories(found)
        return self._in_one_format(found)

    def _in_one_format(self, found: list[Violation]) -> list[Violation]:
        """The violations of one format: those in the files of a format the call does not check are dropped only when
        the graph also found some in the checked format's files, so a finding is not reported once for each mirror. A
        graph that reads only the other format, as it reads a model from its markdown while drawio is checked, keeps
        what it found there, which is then no copy of anything."""
        if not any(violation.location in self._checked_files for violation in found):
            return found
        other_formats = self._other_format_files
        return [violation for violation in found if violation.location not in other_formats]

    def _on_session_stories(self, found: list[Violation]) -> list[Violation]:
        """The violations inside the work's scope, when the session's ticket names its stories: on those stories and on
        everything held under them. A violation on a node of a type a checked practice scopes by stories
        (``PracticeNodeTypes.scope_types``, such as the story map's epics, stories, scenarios, steps, and examples)
        that lies outside them is another increment's work and is left out; files, and every other node, are already
        scoped by the paths the call names."""
        stories = getattr(self._session, "stories", None) or []
        if not stories or self._checked is None:
            return found
        outside: set[str] = set()
        for practice in self._scoped_practices:
            saved = self._checked.practices.get(practice.key)
            scope = practice.reading.types.scope_types
            if saved is not None and scope:
                outside |= saved.outside(stories, scope)
        return [violation for violation in found if violation.node_id not in outside]

    @property
    def _scoped_practices(self) -> list[PracticeGuidance]:
        """The practices whose violations the call reports: those of the fidelities it checks, else every practice of
        the session, as a call that names only graph files reports every practice's violations."""
        checked = list({id(practice): practice for practice in (each.fidelity.practice_guidance for each in self._checked_fidelities)}.values())
        return checked or [output.guidance for output in self._session.session_practices.every.values()]

    @property
    def unread(self) -> list[str]:
        """The paths the call names that gave the graph it built from them no node of a listed practice, such as a
        sketch or a document no graph reading reads: no graph rule ran on them, so a report with no violation says
        nothing about them. None for a graph the call did not build from paths it names."""
        if not self._edited or self._checked is None or self._named not in (None, True):
            return []
        keys = [checked.fidelity.practice_guidance.key for checked in self._checked_fidelities]
        practices = [self._checked.practices[key] for key in keys if key in self._checked.practices]
        files = {node.file.replace("\\", "/") for practice in practices for node in practice.nodes}
        return [path for path in self._edited if not any(file == path or file.startswith(f"{path}/") for file in files)]

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
        if destination in self._files or self._checked is None:
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
        judged = [checked for checked in self._checked_fidelities if (bool(self._files) and checked.fidelity.is_judged_on_graph) == on_graph]
        return "; ".join(checked.judged_files(self._edited) for checked in judged)

    def _graph_files(self) -> list[Path]:
        if self._built_from and self._named in (None, True) and self._checked_fidelities:
            return [self._built_at(self._reports.graph_file())]
        if self._named is True:
            return self._session_saved() or self._built_from_written()
        return self._read_named()

    def _built_from_written(self) -> list[Path]:
        """The session's graph when none is saved yet, "created for the session and loaded when it is missing": built
        from what each listed fidelity has written, so a call naming the session's graph checks it instead of nothing."""
        self._built_from = self._from_session_root(self._written_outputs())
        if not (self._built_from and self._checked_fidelities):
            return []
        return [self._built_at(self._reports.graph_file())]

    def _session_saved(self) -> list[Path]:
        """The session's saved graph, read from the file its graph saves in; none when nothing is saved there."""
        saved_file = self._session.graph.saved_file
        self._checked = saved_file.read()
        return [saved_file.path] if self._checked is not None else []

    def _read_named(self) -> list[Path]:
        """The graph files the call names, one path or several, each read as the graph it holds: one file is checked as
        its graph, and several as one graph of all their violations. None for nothing. Each is named from the project's
        root, or absolute, and one that is not there is refused by name."""
        named = self._named
        entries = [named] if isinstance(named, str) else list(named or [])
        files = [self._session.session_files.existing(str(entry).strip()) for entry in entries if str(entry).strip()]
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
        apart = self._call is not None and self._call.request.answers_a_chat
        self._session.graph.reads.hold_whole(apart)
        self._session.graph.reads.refreshed(self._built_from, destination, apart)
        self._checked = SavedGraph.from_file(destination)
        return destination

    def _from_session_root(self, paths: list[str] | None) -> list[str]:
        """Each named path as graph node files record it, relative to the session's root.

        A relative path is read from the project's checkout, where the agent works and every path it sees starts. The
        session's files refuse a path that is not there, or not under the session's root: the graph would be built
        from nothing, and its empty report would read as a clean validate."""
        return [self._session.session_files.from_root(item) for item in paths or []]

    def _written_outputs(self) -> list[str]:
        """The folders holding what each listed fidelity declares in its checked format and has already written."""
        return sorted({folder for checked in self._checked_fidelities for folder in checked.written_folders})
