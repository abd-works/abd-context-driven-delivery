"""A file of a session, as the viewer shows it: its text, the comments a person wrote on it, what a chat changed in it
for those comments, the folds its classes and members make, and the rules broken in it. Each of those sits on a Range of the file's lines, which returns the text
between them."""

from __future__ import annotations

import posixpath
import re
from difflib import SequenceMatcher
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

from harness.graph.explorer import NodeSource
from harness.graph.graph import Graph, Node, Source
from harness.graph.saved_graph import GRAPH_FILE_NAME, SavedGraph, SavedGraphOutdated
from harness.graph.violation import Violation
from harness.installation.data_class import SourceFile, data_field
from harness.markdown.markdown import MarkdownText

from space.session.file_comments import PROCESSED, FileComment
from space.session.file_manager import FileText
from space.session.file_range import LineSpan, Range
from space.session.file_view_filter import FileViewFilter
from space.session.session_files import NamedPathNotFoundError

if TYPE_CHECKING:
    from space.session.session import Session

FoldKind = Literal["class", "block"]
FileChangeKind = Literal["changed", "added", "removed"]
# How difflib names each kind of change, from the text sent to the text now.
_CHANGE_KINDS: dict[str, FileChangeKind] = {"replace": "changed", "insert": "added", "delete": "removed"}
# A markdown link to another file: its words, the file named from the linking one, and the anchor of the heading it
# names there, when it names one. An image and a web address are not one.
_FILE_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s#:]+)(?:#([^)\s]+))?\)")
# The line of a story test's header that names its story map or its model: ``# Map: ../.context/story-map.md#s-...``.
_HEADER_LINK = re.compile(r"^\s*(?:#|//|\*)\s*(Map|Model):\s*([^\s#:]+)(?:#(\S+))?\s*$")


class Fold:
    """Lines of a file the viewer can fold away: a class whole, or one of its operations or properties as a block, the
    way the graph's source view folds a node's source. The viewer keeps which folds are open."""

    def __init__(self, range: Range, kind: FoldKind, name: str) -> None:
        self._range = range
        self._kind = kind
        self._name = name

    @property
    @data_field
    def range(self) -> Range:
        return self._range

    @property
    @data_field
    def kind(self) -> FoldKind:
        return self._kind

    @property
    @data_field
    def name(self) -> str:
        """The class, operation, or property the fold holds."""
        return self._name


class _FileLink:
    """A link a line of a file writes to another file: the line, the link's words, the file it names from the linking
    one, and the anchor of the heading it names there, when it names one."""

    def __init__(self, line: int, written: re.Match[str]) -> None:
        self.line = line
        self.title, self.file, self.anchor = written.groups(default="")

    @property
    def target(self) -> str:
        """The link's target as the file writes it, such as ``../domain-model.md#cart``."""
        return f"{self.file}#{self.anchor}" if self.anchor else self.file


class FileCallout:
    """A line of a file whose markdown link names another file, or a heading in it, which the viewer opens in place
    under the line, as a call opens in place in code: a story map's story opens its scenarios, and a scenario's domain
    term its class in the markdown model. A link to a file or a heading that is not there opens nothing and says what
    is missing."""

    def __init__(self, link: _FileLink, section: Range, missing: str = "") -> None:
        self._line = link.line
        self._title = link.title
        self._link = link.target
        self._section = section
        self._missing = missing

    @property
    @data_field
    def line(self) -> int:
        """The line, counted from 1, the link sits on."""
        return self._line

    @property
    @data_field
    def title(self) -> str:
        """The link's own words, such as the story's name or the domain term."""
        return self._title

    @property
    @data_field
    def link(self) -> str:
        """The link's target as the file writes it, such as ``../domain-model.md#cart``."""
        return self._link

    @property
    @data_field
    def section(self) -> Range:
        """The linked heading's section, or the whole of a file linked with no heading, in the file it sits in, with
        its text; no lines and no text when it is missing."""
        return self._section

    @property
    @data_field
    def missing(self) -> str:
        """What the link names that is not there, such as ``.context/domain-model.md has no heading #cartline-entity``;
        nothing when the section is there."""
        return self._missing


class FileStep:
    """A step of a story test in the file that reaches code or examples: the line it starts on, where the viewer opens in
    place what it invokes and observes, so a story test's callouts sit on the step whose relationships they are."""

    def __init__(self, line: int, invokes: list[NodeSource], observes: list[NodeSource]) -> None:
        self._line = line
        self._invokes = invokes
        self._observes = observes

    @property
    @data_field
    def line(self) -> int:
        """The line, counted from 1, the step starts on: its decorator or its call."""
        return self._line

    @property
    @data_field
    def invokes(self) -> list[NodeSource]:
        """The functions and operations the step calls, each with its text and file."""
        return list(self._invokes)

    @property
    @data_field
    def observes(self) -> list[NodeSource]:
        """The examples whose state the step observes, each with its text and file."""
        return list(self._observes)


class FileChange:
    """Lines a chat changed in the file, as VS Code and Cursor mark an agent's change: the lines as they read now, and
    the lines they replaced. Lines the chat removed sit on the line now after them, which holds none of their text."""

    def __init__(self, kind: FileChangeKind, range: Range, removed: list[str]) -> None:
        self._kind = kind
        self._range = range
        self._removed = removed

    @property
    @data_field
    def kind(self) -> FileChangeKind:
        return self._kind

    @property
    @data_field
    def range(self) -> Range:
        return self._range

    @property
    @data_field
    def removed(self) -> list[str]:
        """The lines the change replaced or removed, as they read when the comment was sent; none for added lines."""
        return self._removed


class FileViolation:
    """A rule broken on a range of the file."""

    def __init__(self, violation: Violation, range: Range) -> None:
        self._violation = violation
        self._range = range

    @property
    @data_field
    def violation(self) -> Violation:
        return self._violation

    @property
    @data_field
    def range(self) -> Range:
        return self._range


# The most lines the viewer shows of one file. The Files app's editor is as tall as its file, so the page scrolls rather
# than the editor, and it draws every line at once: a file of 90,000 lines left the page answering after 12 seconds and
# one of 360,000 crashed its tab. The longest file of this repository is under half of this.
VIEWER_SHOWS_LINES = 30_000


class FileTooLongToShowError(ValueError):
    """Raised when the viewer asks for a file longer than it shows: drawing it would freeze or crash the page, and with
    it every other open file and comment not yet sent. It carries the file, its lines and the most the viewer shows."""

    def __init__(self, path: str, lines: int, shown: int = VIEWER_SHOWS_LINES) -> None:
        self.path = path
        self.lines = lines
        self.shown = shown
        super().__init__(f"{path} has {lines:,} lines and the viewer shows at most {shown:,}: open it in an editor")


class RuleReads:
    """What a viewer reads on a file: with folds, the folds of its classes and members and no broken rule; with rules,
    the rules the file breaks read on its own; with cross_file, those only the session's whole working copy finds. Any
    of them gives the file's folds; none reads a graph."""

    def __init__(self, rules: bool = False, cross_file: bool = False, folds: bool = False) -> None:
        self.rules = rules
        self.cross_file = cross_file
        self.folds = folds

    @property
    def reads_graph(self) -> bool:
        """Whether the viewer asked for anything a graph places: folds, steps, or broken rules."""
        return self.folds or self.rules or self.cross_file


class SessionFile:
    """A file of the session, named from the project: its text, the comments on it, and, when the viewer asks, its folds
    and the rules it breaks. With rules, the file is read on its own and only its own rules run; with cross_file, the
    session's knowledge graph holds the whole working copy and adds the rules only it finds, linking files and
    practices. Either read gives the folds. A file that is not there, such as one deleted or moved since a page listed
    it, is refused with *NamedPathNotFoundError*: a viewer shown no text would take it for an empty file. A file of more than
    VIEWER_SHOWS_LINES lines is refused with *FileTooLongToShowError*. Its callouts and what its steps reach are those
    shown, the file view's filters deciding which (*FileViewFilter*); a read that sends none holds every one."""

    def __init__(self, session: Session, path: str, reads: RuleReads | None = None, shown: FileViewFilter | None = None) -> None:
        reads = reads or RuleReads()
        self._session = session
        self._shown = shown or FileViewFilter(session)
        self._reads_rules = reads.rules
        self._cross_file = reads.cross_file
        self._reads_graph = reads.reads_graph
        self._text = session.session_files.read(path)
        if not self._text.exists:
            raise NamedPathNotFoundError(path, session.checkout.root)
        lines = self._text.text.count("\n") + 1
        if lines > VIEWER_SHOWS_LINES:
            raise FileTooLongToShowError(self._text.path, lines)
        self._path = self._text.path

    @property
    @data_field
    def path(self) -> Annotated[str, SourceFile]:
        return self._path

    @property
    @data_field
    def text(self) -> str:
        return self._text.text

    @property
    @data_field
    def language(self) -> str:
        return self._text.language

    @property
    @data_field
    def comments(self) -> list[FileComment]:
        return self._session.file_comments.on(self._path)

    @property
    @data_field
    def changes(self) -> list[FileChange]:
        """What the chat changed in this file for the processed comments on it: the file as it read when the first of
        them was sent, against the file now. A change made by hand meanwhile is not told apart from the chat's; none
        once the processed comments are cleared."""
        sent = next((comment.sent_text for comment in self.comments if comment.state == PROCESSED and comment.sent_text), None)
        if sent is None:
            return []
        before, now = sent.splitlines(), self.text.splitlines()
        opcodes = SequenceMatcher(None, before, now, autojunk=False).get_opcodes()
        return [FileChange(_CHANGE_KINDS[tag], self._changed_lines(j1, j2), before[i1:i2]) for tag, i1, i2, j1, j2 in opcodes if tag != "equal"]

    def _changed_lines(self, start: int, end: int) -> Range:
        """The lines now from start to end, counted from 0 and end excluded; removed lines hold none, so they sit on the
        line after them."""
        return self.range(start + 1, end if end > start else start + 1)

    @property
    @data_field
    def folds(self) -> list[Fold]:
        """A fold for each class, operation, and property read in this file, in line order; none while the viewer asks
        for no folds and no rules."""
        if not self._reads_graph:
            return []
        kinds = self._fold_kinds
        nodes = [node for node in self._nodes() if node.type in kinds and node.end_line > node.line]
        folds = [Fold(self.range(node.line, node.end_line), kinds[node.type], node.name) for node in nodes]
        return sorted(folds, key=lambda fold: (fold.range.start_line, -fold.range.end_line))

    @property
    def _fold_kinds(self) -> dict[str, FoldKind]:
        """The node types a file folds on, as the graph's source view does: each practice's classes fold whole, its
        operations and properties as a block (harness/graph/app/source/call-expansion.ts)."""
        readings = [output.guidance.reading for output in self._session.practice_outputs.every.values()]
        members: dict[str, FoldKind] = {kind: "block" for reading in readings for kind in reading.member_types}
        return {**members, **{kind: "class" for reading in readings for kind in reading.class_types}}

    @property
    @data_field
    def steps(self) -> list[FileStep]:
        """Each step of a story test in this file that invokes or observes something the file view's filters show, in
        line order, as the session's graph links it; none while the viewer reads no rules, which never reads a graph,
        or while the graph holds no practice that reads steps."""
        if not (self._reads_rules or self._cross_file):
            return []
        graph = self._session.graph
        steps = (node for practice in graph.practices.opened.values() for node in practice.reading.steps())
        nodes = [node for node in steps if node.source is not None and self._holds(node.source)]
        found = [FileStep(node.source.start_line, self._sources(graph, "invokes", node), self._sources(graph, "observes", node)) for node in nodes]
        return sorted((step for step in found if step.invokes or step.observes), key=lambda step: step.line)

    def _sources(self, graph: Graph, kind: str, node: Node) -> list[NodeSource]:
        """What node reaches by kind that the file view's filters show, each with its source and the class it belongs
        to as its practice names it (``owner_of``)."""
        reached = (edge.child for edge in graph.edges.from_parent(kind, node) if edge.child.source is not None and self._shown.shows(kind, edge.child))
        return [NodeSource(child, owner=child.practice.reading.owner_of(child)) for child in reached]

    def _holds(self, source: Source) -> bool:
        """Whether source, named from its own root, sits in this file."""
        return bool(source.file) and Path(source.root or self._session.work_root, source.file).resolve() == self._session.paths.path_named(self._path)

    @property
    @data_field
    def callouts(self) -> list[FileCallout]:
        """A callout for each markdown link in this file to another file the file view's filters show, in line order:
        the section of the heading it names, or the whole file when it names none, and what is missing when the file
        or the heading is not there.
        A file in another language, such as a story test whose steps link their domain terms, carries a callout only
        for a link to a file that is there, since its code can read as a link (``handlers[name](event)``)."""
        lines = enumerate(self.text.splitlines(), start=1)
        return [callout for number, line in lines for callout in self._callouts_on(number, line)]

    def _callouts_on(self, number: int, line: str) -> list[FileCallout]:
        written = [*_FILE_LINK.finditer(line), *_HEADER_LINK.finditer(line)]
        found = (self._callout(_FileLink(number, link)) for link in written)
        return [callout for callout in found if callout is not None]

    def _callout(self, link: _FileLink) -> FileCallout | None:
        """The callout of link, whose file is named from this one; none for a link out of the project, one in code to a
        file not there, or one into a file the file view's filters leave out. A file not there is in no list, so no
        filter hides the callout that says so."""
        target = posixpath.normpath(posixpath.join(posixpath.dirname(self._path), link.file))
        if target.startswith(".."):
            return None
        linked = self._session.session_files.read(target)
        if not linked.exists:
            return FileCallout(link, Range(target, LineSpan(0, 0), ""), f"{target} is not there") if self.language == "markdown" else None
        if not self._shown.shows_file(target):
            return None
        lines = self._lines_linked(linked, link.anchor)
        if lines is None:
            return FileCallout(link, Range(linked.path, LineSpan(0, 0), ""), f"{linked.path} has no heading #{link.anchor}")
        return FileCallout(link, Range.of_text(linked.path, linked.text, LineSpan(*lines)))

    def _lines_linked(self, linked: FileText, anchor: str) -> tuple[int, int] | None:
        """The lines of linked a link opens: the section under the heading anchor names in a markdown file, the whole
        file when the link names no heading or the file is in another language; none when no heading has that anchor."""
        if anchor and linked.language == "markdown":
            return MarkdownText(linked.text).anchored_lines(anchor)
        return 1, max(1, len(linked.text.splitlines()))

    @property
    @data_field
    def violations(self) -> list[FileViolation]:
        """Each rule broken in this file, on the lines it names, one naming no line covering the first: with rules, those
        its own read finds and the session's last validate saved; with cross_file, those only the whole working copy
        finds."""
        own = self._own_violations() if self._reads_rules else []
        found = self._unique([*own, *(self._cross_file_violations() if self._cross_file else [])])
        return [FileViolation(violation, self.range(violation.line or 1, violation.end_line or violation.line or 1)) for violation in found]

    def range(self, start_line: int, end_line: int) -> Range:
        """Lines start_line to end_line of this file, with the text they hold now."""
        return Range.of_text(self._path, self.text, LineSpan(start_line, end_line))

    def _nodes(self) -> list:
        """This file's nodes as its own read found them, else as the session's last validate saved them."""
        return self._in_this_file(self._alone, self._alone_folder) or self._in_this_file(self._last_validate)

    def _own_violations(self) -> list[Violation]:
        """What reading the file on its own finds broken, and what the session's last validate saved, which can hold a
        rule a validating agent judged."""
        alone = [violation for violation in self._alone.violations() if self._is_this_file(violation.location, self._alone_folder)]
        validated = [violation for violation in (self._last_validate.violations() if self._last_validate else []) if self._is_this_file(violation.location)]
        return [*alone, *validated]

    def _cross_file_violations(self) -> list[Violation]:
        """What the whole working copy finds broken in this file that reading it alone does not."""
        alone = {self._key(violation) for violation in self._alone.violations()}
        return [violation for violation in self._whole.violations() if self._is_this_file(violation.location) and self._key(violation) not in alone]

    def _unique(self, violations: list[Violation]) -> list[Violation]:
        """Each broken rule once, however many reads found it on the same lines."""
        seen: set[tuple] = set()
        kept = []
        for violation in violations:
            if self._key(violation) not in seen:
                seen.add(self._key(violation))
                kept.append(violation)
        return kept

    def _key(self, violation: Violation) -> tuple:
        return (violation.rule, violation.line, violation.end_line, violation.message)

    def _in_this_file(self, graph: SavedGraph | None, folder: Path | None = None) -> list:
        return [node for practice in graph.practices.values() for node in practice.nodes if self._is_this_file(node.file, folder)] if graph else []

    @property
    def _alone_folder(self) -> Path:
        """The folder the file read on its own names its nodes' files from: the project's root."""
        return self._session.file_graphs.alone_folder

    @cached_property
    def _alone(self) -> SavedGraph:
        return self._session.file_graphs.file_alone(self._session.paths.path_named(self._path))

    @cached_property
    def _whole(self) -> SavedGraph:
        is_held = bool(self._in_this_file(SavedGraph.from_graph(self._session.graph)))
        return self._session.file_graphs.file_in_whole(self._session.paths.path_named(self._path), is_held)

    @cached_property
    def _last_validate(self) -> SavedGraph | None:
        """What the session's last validate saved; none before it saved a graph, or one in a shape the graph no longer
        writes, which the next validate writes again."""
        saved = Path(self._session.work_folder) / GRAPH_FILE_NAME
        if not saved.is_file():
            return None
        try:
            return SavedGraph.from_file(saved)
        except SavedGraphOutdated:
            return None

    def _is_this_file(self, named: str, folder: Path | None = None) -> bool:
        """Whether named, as a graph names a file (from folder, the session's root by default, or absolute), is this
        file."""
        if not named:
            return False
        path = Path(named)
        located = path if path.is_absolute() else Path(folder or self._session.work_root) / path
        return located.resolve() == self._session.paths.path_named(self._path)
