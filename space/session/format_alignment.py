"""Format alignment - whether the formats a session chose for each fidelity say the same thing, and bringing them in step.

A fidelity is written in several formats: a story map as markdown, as a draw.io drawing and as a whiteboard. A person or
an agent changes one of them and the others fall behind. *SessionAlignment* goes through the session's guidance
selection (the stages and practices selected, and the formats chosen for each fidelity they cover), reads each format's
file through the render action and the knowledge graph, and answers every gap in plain words (``diagnose``); ``align``
then renders the format that lacks from the format that holds more.

Which format is the source when two differ:

- A chosen format with no file is rendered from the fidelity's leading format, the first of its chosen formats that
  is written as a document (markdown), else the first chosen, when that file is there; else from the first chosen
  format whose file is there.
- Two files that differ, where one holds every node and edge the other holds and more, are aligned from the one that
  holds more to the one that lacks.
- Two files that each hold something the other lacks are a person's decision: the gap is reported, naming what each
  holds alone, and both files are left as they are. So is every other format of that document: while two of its files
  conflict, none of its files is aligned, since the file a render would read from may be the one that is wrong.

Align saves through the Render action alone, so a drawing keeps the layout people gave it and a document the words its
source does not hold, as every render does. A chosen code format with no file is rendered too, from the first chosen
format whose file is there, a document before a drawing, into the files the fidelity declares for that format. A code
file already there is never replaced: the Render action writes the new shape onto it and keeps every line it held, and
each aligned file names the members that wait to be migrated in it. Code that is there is not compared with the
documents, so no gap says a code file lacks what a document holds.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from cdd_guidance.actions.render.render import Render
from cdd_guidance.actions.render.rendered_file import SAVED_GROUPS
from harness.agent_tools.agent_tools import agent_tool, noSessionLog
from harness.agent_tools.tool_call import ToolCall
from harness.annotations.annotation import hosted_only
from harness.diagnostics.probe_outcome import raised_by_a_bug
from harness.graph.graph import Graph
from harness.graph.saved_graph import SavedGraph, SavedPractice
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from harness.installation.data_class import data_field
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import long_call, mcp
from space.session.callout_alignment import CalloutAlignment
from space.session.guidance_selection import GuidanceSelection

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from space.session.session import Session

# The kinds of gap a diagnosis reports. The first two are aligned by a render; the rest wait for a person or a fix.
MISSING_FILE = "missing_file"
FORMAT_LACKS = "format_lacks"
FORMATS_CONFLICT = "formats_conflict"
NOT_COMPARED = "not_compared"
UNREADABLE_FORMAT = "unreadable_format"
# The kinds of failure an alignment answers.
RENDER_FAILED = "render_failed"
# The format group written as a document, which the graph reads and so leads a comparison.
_DOCUMENT_GROUP = "markdown"
# How many names a gap's message spells out before it counts the rest.
_NAMED_IN_MESSAGE = 5


class AlignmentGap:
    """One gap a diagnosis found, in plain words: its kind, the fidelity and the file it is in, the file it can be
    aligned from when a render closes it, and the nodes and edges the file lacks."""

    def __init__(self, kind: str, fidelity: str, file: str, message: str, format: str = "", source: str = "", lacks: GraphDifference | None = None) -> None:
        self._kind = kind
        self._fidelity = fidelity
        self._file = file
        self._message = message
        self._format = format
        self._source = source
        self._lacks = lacks or GraphDifference(set(), set())

    @property
    @data_field
    def kind(self) -> str:
        """What is wrong: ``missing_file``, ``format_lacks``, ``formats_conflict``, ``not_compared``,
        ``unreadable_format``, ``callout_target_missing``, ``callout_without_edge`` or ``edge_without_callout``."""
        return self._kind

    @property
    @data_field
    def fidelity(self) -> str:
        """The slug of the fidelity the gap is in, such as stories-story-map; empty for a callout's gap."""
        return self._fidelity

    @property
    @data_field
    def file(self) -> str:
        """The file the gap is in, named from the project."""
        return self._file

    @property
    @data_field
    def format(self) -> str:
        """The format of that file, which an alignment renders into; empty for a callout's gap."""
        return self._format

    @property
    @data_field
    def source(self) -> str:
        """The file an alignment renders from, named from the project; empty when a person decides or nothing renders it."""
        return self._source

    @property
    @data_field
    def is_alignable(self) -> bool:
        """Whether a render closes the gap: it names the file the render reads from."""
        return bool(self._source)

    @property
    @data_field
    def missing_nodes(self) -> list[str]:
        """The nodes the file lacks that the other format holds, each as its type and name."""
        return self._lacks.node_names

    @property
    @data_field
    def missing_edges(self) -> list[str]:
        """The edges the file lacks that the other format holds, each as its two nodes and its kind."""
        return self._lacks.edge_names

    @property
    @data_field
    def message(self) -> str:
        return self._message

    def left_to_a_person(self) -> AlignmentGap:
        """This gap with no source to align from, because another format of its document conflicts with one of them."""
        message = f"{self._message} It is left as it is until a person settles the formats of this document that conflict."
        return AlignmentGap(self._kind, self._fidelity, self._file, message, self._format, lacks=self._lacks)


class AlignmentFailure:
    """One failure an alignment met, as data a Fix button sends on: its kind, the file it was writing, and what was said."""

    def __init__(self, kind: str, file: str, message: str) -> None:
        self._kind = kind
        self._file = file
        self._message = message

    @property
    @data_field
    def kind(self) -> str:
        """``render_failed``: the render raised, such as code the fidelity's declared paths cannot place, or a render
        that would lose a line a file holds."""
        return self._kind

    @property
    @data_field
    def file(self) -> str:
        return self._file

    @property
    @data_field
    def message(self) -> str:
        return self._message


class AlignedFile:
    """One file an alignment rendered: the file saved, its format, the file it was rendered from, and what is left for
    an agent to do with it, such as publishing a whiteboard to its board."""

    def __init__(self, file: str, format: str, source: str, migrate: list[str] | None = None) -> None:
        self._file = file
        self._format = format
        self._source = source
        self._migrate = list(migrate or [])

    @property
    @data_field
    def file(self) -> str:
        return self._file

    @property
    @data_field
    def format(self) -> str:
        return self._format

    @property
    @data_field
    def source(self) -> str:
        return self._source

    @property
    @data_field
    def migrate(self) -> list[str]:
        """The members the file keeps though its model no longer holds them, such as ``Cart.total``: each waits for its
        body to be moved into the member that replaced it."""
        return list(self._migrate)

    @property
    @data_field
    def follow_up(self) -> str:
        """What the render leaves to an agent: a whiteboard file is put on its board in Claude by render.publish_board,
        and a code file's members no longer in the model are migrated."""
        if self._migrate:
            return f"Migrate in {self._file}: {', '.join(self._migrate)} is no longer in the model and is kept there, marked; move its body into the member that replaced it, then delete it."
        return f"Publish {self._file} to its board in Claude (render.publish_board)." if self._format == "whiteboard" else ""


class AlignmentDiagnosis:
    """What a diagnosis found in one session: the fidelities it went through and every gap, in the order found."""

    def __init__(self, fidelities: list[str], gaps: list[AlignmentGap]) -> None:
        self._fidelities = list(fidelities)
        self._gaps = list(gaps)

    @property
    @data_field
    def fidelities(self) -> list[str]:
        """The slugs of the fidelities checked: those the selected stages and practices cover."""
        return list(self._fidelities)

    @property
    @data_field
    def gaps(self) -> list[AlignmentGap]:
        return list(self._gaps)

    @property
    @data_field
    def is_aligned(self) -> bool:
        return not self._gaps


class AlignmentResult:
    """What an alignment did: each file it rendered, each failure it met, and the diagnosis as it stands afterwards."""

    def __init__(self, aligned: list[AlignedFile], failures: list[AlignmentFailure], diagnosis: AlignmentDiagnosis) -> None:
        self._aligned = list(aligned)
        self._failures = list(failures)
        self._diagnosis = diagnosis

    @property
    @data_field
    def aligned(self) -> list[AlignedFile]:
        return list(self._aligned)

    @property
    @data_field
    def failures(self) -> list[AlignmentFailure]:
        return list(self._failures)

    @property
    @data_field
    def diagnosis(self) -> AlignmentDiagnosis:
        """The gaps still there after the renders: those a person decides, and those a failure left open."""
        return self._diagnosis


class GraphDifference:
    """The nodes and edges one graph reading holds and another lacks, each named as a person reads it."""

    def __init__(self, nodes: set[tuple[str, str]], edges: set[tuple[str, str, str]]) -> None:
        self._nodes = nodes
        self._edges = edges

    def __bool__(self) -> bool:
        return bool(self._nodes or self._edges)

    @property
    def node_names(self) -> list[str]:
        return [f"{type} '{name}'" for type, name in sorted(self._nodes)]

    @property
    def edge_names(self) -> list[str]:
        return [f"{parent} {kind} {child}" for kind, parent, child in sorted(self._edges)]

    @property
    def described(self) -> str:
        """The difference in a sentence's worth of words: the first few nodes and edges by name, then how many more."""
        names = self.node_names + [f"the edge {edge}" for edge in self.edge_names]
        more = len(names) - _NAMED_IN_MESSAGE
        return ", ".join(names[:_NAMED_IN_MESSAGE]) + (f" and {more} more" if more > 0 else "")


class GraphReading:
    """What the knowledge graph reads from one document: its nodes, each by type and name, and the edges between them,
    each by kind and the two nodes it joins. Two readings are compared by those names, never by the lines or ids a
    format happens to give them."""

    def __init__(self, practice: SavedPractice) -> None:
        named = {node.node_id: (node.type, node.name) for node in practice.nodes}
        self._nodes = set(named.values())
        joined = [edge for edge in practice.edges if edge.parent in named and edge.child in named]
        self._edges = {(edge.kind, "{} '{}'".format(*named[edge.parent]), "{} '{}'".format(*named[edge.child])) for edge in joined}

    @property
    def is_empty(self) -> bool:
        return not self._nodes

    def lacking_from(self, other: GraphReading) -> GraphDifference:
        """What other holds that this reading lacks."""
        return GraphDifference(other._nodes - self._nodes, other._edges - self._edges)


class _ComparisonGraph:
    """The graph a diagnosis reads each format's document into, apart from the session's knowledge graph: its own
    instance of every practice, made once, and a folder of its own that holds one document at a time. A format the
    graph does not read itself, such as a whiteboard, is first rendered into the fidelity's leading format, so every
    format is read by the same reader."""

    def __init__(self) -> None:
        self._graph: Graph | None = None
        self._folder: Path | None = None

    def reading(self, practice: PracticeGuidance, text: str, placed_at: str) -> GraphReading:
        """What practice's graph reading reads from text, a document placed at placed_at, its path from the project."""
        graph, folder = self._opened()
        document = folder / placed_at
        document.parent.mkdir(parents=True, exist_ok=True)
        document.write_text(text, encoding="utf-8")
        try:
            graph.load_files(str(folder), [practice.key], [placed_at])
            return GraphReading(SavedGraph.from_graph(graph).practices.get(practice.key) or SavedPractice(practice.key))
        finally:
            document.unlink()

    def close(self) -> None:
        """Remove the folder the documents were read from."""
        if self._folder is not None:
            shutil.rmtree(self._folder, ignore_errors=True)
        self._graph, self._folder = None, None

    def _opened(self) -> tuple[Graph, Path]:
        if self._graph is None or self._folder is None:
            self._graph = Graph(PRACTICE_CATALOGUE.create_all())
            self._folder = Path(tempfile.mkdtemp(prefix="cdd-format-alignment-"))
        return self._graph, self._folder


class _FidelityAlignment:
    """One fidelity's chosen formats in a session, document by document: the file each format is written to, whether it
    is there, and whether the graph reads the same nodes and edges from each."""

    def __init__(self, fidelity: FidelityGuidance, session: Session, comparison: _ComparisonGraph) -> None:
        self._fidelity = fidelity
        self._session = session
        self._comparison = comparison
        self._output = fidelity.session_output

    def gaps(self) -> list[AlignmentGap]:
        """Every gap between this fidelity's chosen formats: for each document, a format whose file is missing, then
        each file that lacks what another holds; then a chosen code format with no file at all."""
        found = [gap for files in self._documents() for gap in self._document_gaps(files)]
        return found + self._code_formats_missing()

    @property
    def _compared_formats(self) -> list[str]:
        """The chosen formats a render saves, a document format first: the leading format, then the rest as chosen."""
        saved = [name for name in self._output.chosen_formats if Format(name).group in SAVED_GROUPS]
        return sorted(saved, key=lambda name: Format(name).group != _DOCUMENT_GROUP)

    def _documents(self) -> list[dict[str, Path]]:
        """Each document of the fidelity as the file every compared format writes it to, by format: the files the
        fidelity declares beside one another (``WrittenFiles.saved_beside``), found from each file that is there."""
        formats = self._compared_formats
        if len(formats) < 2:
            return []
        leading, listed = formats[0], self._output.written.files()
        there = [(name, self._session.paths.path_named(entry.path)) for name in formats for entry in listed.get(name, []) if entry.exists]
        leads = [file if name == leading else self._beside(file, leading) for name, file in there]
        documents = {lead: {leading: lead, **self._others_beside(lead, formats[1:])} for lead in dict.fromkeys(leads) if lead is not None}
        return [files for files in documents.values() if len(files) > 1]

    def _others_beside(self, lead: Path, formats: list[str]) -> dict[str, Path]:
        placed = ((name, self._beside(lead, name)) for name in formats)
        return {name: file for name, file in placed if file is not None}

    def _beside(self, file: Path, format: str) -> Path | None:
        """The file the fidelity writes format to for the document file is of, as a render of file places it: where
        the fidelity declares it, else beside file under the name the fidelity writes format to; none when it names
        none."""
        declared = self._fidelity.declared
        named = declared.file_name_beside(file.as_posix(), format)
        return self._output.written.saved_beside(file, format) or (file.parent / named if named else None)

    def _document_gaps(self, files: dict[str, Path]) -> list[AlignmentGap]:
        there = {name: file for name, file in files.items() if file.is_file()}
        source = next(iter(there.values()))
        missing = [self._missing(name, file, source) for name, file in files.items() if name not in there]
        gaps = missing + self._differences(there, placed_at=self._named(next(iter(files.values()))))
        if any(gap.kind == FORMATS_CONFLICT for gap in gaps):
            return [gap.left_to_a_person() if gap.is_alignable else gap for gap in gaps]
        return gaps

    def _missing(self, format: str, file: Path, source: Path) -> AlignmentGap:
        message = f"{self._fidelity.slug} has {format} chosen, but {self._named(file)} is not there. Align renders it from {self._named(source)}."
        return AlignmentGap(MISSING_FILE, self._fidelity.slug, self._named(file), message, format, self._named(source))

    def _differences(self, there: dict[str, Path], placed_at: str) -> list[AlignmentGap]:
        """The gaps between the files that are there: each file read into a graph, then every other compared with the
        first. A file whose render fails is reported as unreadable and compared with nothing."""
        readings: dict[str, GraphReading] = {}
        gaps: list[AlignmentGap] = []
        for name, file in there.items():
            read = self._read(name, file, next(iter(there)), placed_at)
            if isinstance(read, AlignmentGap):
                gaps.append(read)
            else:
                readings[name] = read
        if len(readings) < 2:
            return gaps
        (first, leading), *others = readings.items()
        return gaps + [gap for name, reading in others for gap in self._compared(there[first], leading, there[name], reading, (first, name))]

    def _read(self, format: str, file: Path, leading: str, placed_at: str) -> GraphReading | AlignmentGap:
        """The graph's reading of file: its own text in the leading format, else its render into the leading format.
        A failure the render declares is answered as a gap; a programming error raises."""
        try:
            text = file.read_text(encoding="utf-8") if format == leading else str(self._fidelity.render_files(leading, [str(file)], format)["content"])
            return self._comparison.reading(self._fidelity.practice_guidance, text, placed_at)
        except Exception as failure:
            if raised_by_a_bug(failure):
                raise
            message = f"{self._named(file)} cannot be read as {leading}: {type(failure).__name__}: {failure}"
            return AlignmentGap(UNREADABLE_FORMAT, self._fidelity.slug, self._named(file), message, format)

    def _compared(self, lead: Path, leading: GraphReading, other: Path, reading: GraphReading, formats: tuple[str, str]) -> list[AlignmentGap]:
        """The gap between two files of one document, if any: nothing read from either, one lacking what the other
        holds, or each holding something alone."""
        slug, lead_name, other_name = self._fidelity.slug, self._named(lead), self._named(other)
        if leading.is_empty and reading.is_empty:
            return [AlignmentGap(NOT_COMPARED, slug, other_name, f"The graph reads no node from {lead_name} or {other_name}, so they are not compared.", formats[1])]
        other_lacks, lead_lacks = reading.lacking_from(leading), leading.lacking_from(reading)
        if other_lacks and lead_lacks:
            message = (
                f"{lead_name} and {other_name} each hold what the other lacks: only {lead_name} holds {other_lacks.described}; "
                f"only {other_name} holds {lead_lacks.described}. A person decides which is right; both files are left as they are."
            )
            return [AlignmentGap(FORMATS_CONFLICT, slug, other_name, message, formats[1], lacks=other_lacks)]
        if other_lacks:
            return [self._lacks(other_name, formats[1], lead_name, other_lacks)]
        return [self._lacks(lead_name, formats[0], other_name, lead_lacks)] if lead_lacks else []

    def _lacks(self, file: str, format: str, source: str, lacks: GraphDifference) -> AlignmentGap:
        message = f"{file} lacks {lacks.described}, which {source} holds. Align renders {file} from {source}."
        return AlignmentGap(FORMAT_LACKS, self._fidelity.slug, file, message, format, source, lacks)

    def _code_formats_missing(self) -> list[AlignmentGap]:
        """A chosen code format with no file, in a fidelity another chosen format already has a file of: aligned from
        the first of those files, a document before a drawing. A format written as a folder of code for each module
        lists only what the session's branch changed, so it is not judged."""
        listed = self._output.written.files()
        chosen = sorted(self._output.chosen_formats, key=lambda name: Format(name).group != _DOCUMENT_GROUP)
        there = [entry.path for name in chosen for entry in listed.get(name, []) if entry.exists]
        if not there:
            return []
        paths = self._output.written.output_paths()
        unsaved = [name for name in chosen if Format(name).group not in SAVED_GROUPS and not any(path.endswith("/") for path in paths.get(name, []))]
        return [self._code_missing(name, paths.get(name, []), there[0]) for name in unsaved if not any(entry.exists for entry in listed.get(name, []))]

    def _code_missing(self, format: str, declared: list[str], source: str) -> AlignmentGap:
        place = self._named(declared[0]) if declared else ""
        message = f"{self._fidelity.slug} has {format} chosen, but no {format} file is there. Align renders it from {source}, one file for each piece at {place}."
        return AlignmentGap(MISSING_FILE, self._fidelity.slug, place, message, format, source)

    def _named(self, file: Path | str) -> str:
        return self._session.paths.from_project(file)


class SessionAlignment:
    """The alignment of one session's formats: its diagnosis, and the renders that close the gaps a render can close.
    It holds the session, and for an alignment the call it answers, which the Render action logs its lines for."""

    def __init__(self, session: Session, call: ToolCall | None = None) -> None:
        self._session = session
        self._call = call

    def diagnose(self) -> AlignmentDiagnosis:
        """Go through every fidelity the session's selected stages and practices cover and answer each gap: a chosen
        format with no file, formats of one document the graph reads differently, and callouts that match no edge of
        the session's graph, or edges no callout shows."""
        # A diagnosis reads the files as they are now: a search made a moment ago does not hold a file written since,
        # such as one an alignment just rendered.
        self._session.session_files.file_manager.search_again()
        covered = GuidanceSelection(self._session).covered
        comparison = _ComparisonGraph()
        try:
            gaps = [gap for fidelity in covered for gap in _FidelityAlignment(fidelity, self._session, comparison).gaps()]
        finally:
            comparison.close()
        callouts = CalloutAlignment(self._session, self._files_of(covered), self._call)
        return AlignmentDiagnosis([fidelity.slug for fidelity in covered], gaps + [self._callout_gap(*gap) for gap in callouts.gaps()])

    def align(self) -> AlignmentResult:
        """Render each file a diagnosis says a render closes, from the source the gap names, then diagnose again. Each
        failure is answered as data and the next gap is still worked."""
        aligned: list[AlignedFile] = []
        failures: list[AlignmentFailure] = []
        for gap in (gap for gap in self.diagnose().gaps if gap.is_alignable):
            done = self._rendered(gap, Render(self._session, self._call))
            aligned += [each for each in done if isinstance(each, AlignedFile)]
            failures += [each for each in done if isinstance(each, AlignmentFailure)]
        return AlignmentResult(aligned, failures, self.diagnose())

    def _rendered(self, gap: AlignmentGap, render: Render) -> list[AlignedFile | AlignmentFailure]:
        """Each file the render of gap's source into its format saved, or the failure it met. A failure the render
        declares, such as an empty source or code its fidelity's declared paths cannot place, is answered; a
        programming error raises."""
        try:
            results = [result for result in render.render([gap.fidelity], gap.format, [gap.source]) if isinstance(result, dict)]
        except Exception as failure:
            if raised_by_a_bug(failure):
                raise
            return [AlignmentFailure(RENDER_FAILED, gap.file, f"Rendering {gap.source} to {gap.format} failed: {type(failure).__name__}: {failure}")]
        saved = [path for result in results for path in ([result["path"]] if result.get("path") else result.get("paths", []))]
        waiting = [(each["file"], each.get("kept") or each.get("signature_differs")) for result in results for each in result.get("migrate", [])]
        return [AlignedFile(self._session.paths.from_project(path), gap.format, gap.source, [kept for file, kept in waiting if file == path]) for path in saved]

    def _files_of(self, covered: Iterable[FidelityGuidance]) -> list[str]:
        """The files that are there of the chosen formats of the fidelities covered, each once, named from the project."""
        listed = ((fidelity.session_output.chosen_formats, fidelity.session_output.written.files()) for fidelity in covered)
        return list(dict.fromkeys(entry.path for chosen, files in listed for name in chosen for entry in files.get(name, []) if entry.exists))

    def _callout_gap(self, kind: str, file: str, message: str) -> AlignmentGap:
        return AlignmentGap(kind, "", file, message)


@hosted_only
class SessionAlignmentTools:
    """The tools that diagnose and align a session's formats, each asking its *SessionAlignment*."""

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def diagnose_alignment(self, call: ToolCall | None = None) -> AlignmentDiagnosis:
        """Return every gap between this session's formats, changing no file: for each fidelity its selected stages and practices cover, a chosen format whose file is not there; two formats of one document the knowledge graph reads differently, naming the nodes and edges one holds and the other lacks; and, in its markdown files, a callout whose target is not there, a callout no edge of the graph matches, and an edge to another file that no callout shows. Each gap says in plain words what is wrong, and names the source file when align_formats closes it. The session's graph reads the files of the chosen formats, as session.graph_trees does."""
        return SessionAlignment(self, call).diagnose()

    @long_call
    @mcp
    @agent_tool
    def align_formats(self, call: ToolCall | None = None) -> AlignmentResult:
        """Bring this session's formats in step and return what was done: render each chosen format whose file is missing, and each file that lacks nodes or edges another format of the same document holds, from the format that holds more, through the Render action, so a drawing keeps its layout and a document its own words. Two files that each hold something the other lacks are a person's decision and are left as they are. Each failure a render meets is answered as kind, file and message, and the rest are still rendered; the diagnosis as it stands afterwards comes back too. A whiteboard file rendered here still has to be put on its board in Claude (render.publish_board)."""
        return SessionAlignment(self, call).align()
