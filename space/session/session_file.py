"""A file of a session, as the viewer shows it: its text, the comments a person wrote on it, what a chat changed in it
for those comments, the folds its classes and members make, and the rules broken in it. Each of those sits on a Range of the file's lines, which returns the text
between them."""

from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

from harness.graph.saved_graph import GRAPH_FILE_NAME, SavedGraph, SavedGraphOutdated
from harness.graph.violation import Violation
from harness.installation.data_class import SourceFile, data_field

from space.session.file_comments import PROCESSED, FileComment
from space.session.file_range import Range

if TYPE_CHECKING:
    from space.session.session import Session

FoldKind = Literal["class", "block"]
FileChangeKind = Literal["changed", "added", "removed"]
# How difflib names each kind of change, from the text sent to the text now.
_CHANGE_KINDS: dict[str, FileChangeKind] = {"replace": "changed", "insert": "added", "delete": "removed"}
# The node types a graph folds on, as the graph's source view does: a class folds whole, each operation and property as
# a block (harness/graph/app/source/call-expansion.ts). The classes are Clean Engineering's and DDD's class types.
CLASS_TYPES = frozenset({"OoadClass", "Aggregate", "DomainEvent", "EntityRoot", "Entity", "ValueObject", "Repository", "DomainService", "Factory", "Specification"})
MEMBER_TYPES = frozenset({"Operation", "Property"})


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


class SessionFile:
    """A file of the session, named from the project: its text, the comments on it, its folds, and its violations.
    Folds and violations come from the graph the session last saved, so a file the graph never read has none."""

    def __init__(self, session: Session, path: str) -> None:
        self._session = session
        self._text = session.session_files.read(path)
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
        return [self._change(_CHANGE_KINDS[tag], before[i1:i2], j1, j2) for tag, i1, i2, j1, j2 in opcodes if tag != "equal"]

    def _change(self, kind: FileChangeKind, removed: list[str], start: int, end: int) -> FileChange:
        """The change on the lines now from start to end, counted from 0 and end excluded; removed lines hold none, so
        they sit on the line after them."""
        return FileChange(kind, self.range(start + 1, end if end > start else start + 1), removed)

    @property
    @data_field
    def folds(self) -> list[Fold]:
        """A fold for each class, operation, and property the session's graph places in this file, in line order."""
        nodes = [node for node in self._saved_nodes() if node.type in CLASS_TYPES | MEMBER_TYPES]
        folds = [Fold(self.range(node.line, node.end_line), "class" if node.type in CLASS_TYPES else "block", node.name) for node in nodes if node.end_line > node.line]
        return sorted(folds, key=lambda fold: (fold.range.start_line, -fold.range.end_line))

    @property
    @data_field
    def violations(self) -> list[FileViolation]:
        """Each rule the session's graph found broken in this file, on the lines it names; one naming no line covers
        the first."""
        graph = self._saved_graph()
        found = [violation for violation in (graph.violations() if graph else []) if self._is_this_file(violation.location)]
        return [FileViolation(violation, self.range(violation.line or 1, violation.end_line or violation.line or 1)) for violation in found]

    def range(self, start_line: int, end_line: int) -> Range:
        """Lines start_line to end_line of this file, with the text they hold now."""
        return Range.of_text(self._path, self.text, start_line, end_line)

    def _saved_nodes(self):
        graph = self._saved_graph()
        return [node for practice in (graph.practices.values() if graph else []) for node in practice.nodes if self._is_this_file(node.file)]

    def _saved_graph(self) -> SavedGraph | None:
        """The graph saved in the session's folder; none before the session has saved one, or when it was saved in a
        shape the graph no longer writes."""
        saved = Path(self._session.session_path) / GRAPH_FILE_NAME
        if not saved.is_file():
            return None
        try:
            return SavedGraph.from_file(saved)
        except SavedGraphOutdated:
            return None

    def _is_this_file(self, named: str) -> bool:
        """Whether named, as the graph names a file (from the session's root, or absolute), is this file."""
        if not named:
            return False
        path = Path(named)
        located = path if path.is_absolute() else Path(self._session.work_root) / path
        return located.resolve() == self._session.path_named(self._path)
