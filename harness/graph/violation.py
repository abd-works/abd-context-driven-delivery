"""One place a rule is broken. A graph rule records it on the node it checked, the saved graph keeps it as the same
data ``graph.return_nodes`` sends, the explorer shows it under the node's rule, and the validation report and the board
read it back from the saved graph."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, TypedDict

from harness.graph.location import Location
from harness.installation.data_class import SourceFile, data_field

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.graph_rules_collection import GraphRule

# A judgment or scanner that cannot tie its finding to a file names this place.
UNKNOWN_LOCATION = "unknown"


class SourceLine:
    """One numbered line of the file a violation names."""

    def __init__(self, number: int, text: str) -> None:
        self._number = number
        self._text = text

    @property
    @data_field
    def number(self) -> int:
        return self._number

    @property
    @data_field
    def text(self) -> str:
        return self._text


class SourceLineData(TypedDict):
    """A SourceLine as ``data_of`` sends it."""

    number: int
    text: str


class ViolationData(TypedDict, total=False):
    """A violation as ``data_of`` sends it for ``graph.return_nodes`` and writes it in the saved graph."""

    rule: str
    message: str
    practice: str
    node_id: str
    subject: str
    location: str
    line: int | None
    end_line: int | None
    severity: str
    source: list[SourceLineData]


class FoundOn:
    """The node a violation was found on: its id and what it is (``Operation `checkout```); a finding that names no
    node leaves both out."""

    def __init__(self, node_id: str = "", subject: str = "") -> None:
        self.node_id = node_id
        self.subject = subject


NO_NODE = FoundOn()


class FoundBy:
    """What found a violation: the rule, the practice that checks it, and the node it was found on, when it names
    one."""

    def __init__(self, rule: str, practice: str = "", found_on: FoundOn = NO_NODE) -> None:
        self.rule = rule
        self.practice = practice
        self.found_on = found_on


# A violation is an error: no rule reports a lesser severity.
SEVERITY = "error"
# How many lines before and after a violation's own a reader is shown with it.
QUOTED_LINES_BEFORE = 2
QUOTED_LINES_AFTER = 4
NOWHERE = Location()


class Violation:
    """A rule broken at one place: what found it (the rule, the practice that checks it, and the node it was found on),
    the message, and the file and lines (``location``). A finding that names no node, such as a draw.io scanner's or a judged
    rule's, leaves the node out; one that names no file is at ``unknown``."""

    def __init__(self, found_by: FoundBy, message: str, location: Location = NOWHERE) -> None:
        self._found_by = found_by
        self._message = (message or "").strip()
        self._location = location
        self._source: list[SourceLine] = []

    @classmethod
    def from_data(cls, sent: ViolationData) -> Violation:
        """A violation sent as data, the way ``data_of`` writes it for ``graph.return_nodes`` and the saved graph."""
        found_on = FoundOn(str(sent.get("node_id") or ""), str(sent.get("subject") or ""))
        found_by = FoundBy(str(sent.get("rule") or ""), str(sent.get("practice") or ""), found_on)
        location = Location(str(sent.get("location") or ""), sent.get("line"), sent.get("end_line"))
        return cls(found_by, str(sent.get("message") or ""), location)

    @property
    @data_field
    def rule(self) -> str:
        return self._found_by.rule

    @property
    @data_field
    def practice(self) -> str:
        return self._found_by.practice

    @property
    @data_field
    def node_id(self) -> str:
        return self._found_by.found_on.node_id

    @property
    @data_field
    def subject(self) -> str:
        """What the node the violation was found on is, such as ``Operation `checkout```; empty when it names no node."""
        return self._found_by.found_on.subject

    @property
    @data_field
    def location(self) -> Annotated[str, SourceFile]:
        return self._location.file or UNKNOWN_LOCATION

    @property
    @data_field
    def line(self) -> int | None:
        return int(self._location.line) if self._location.line else None

    @property
    @data_field
    def end_line(self) -> int | None:
        return int(self._location.end_line) if self._location.end_line else self.line

    @property
    @data_field
    def message(self) -> str:
        return self._message

    @property
    @data_field
    def severity(self) -> str:
        return SEVERITY

    @property
    @data_field
    def source(self) -> list[SourceLine]:
        """The lines around the violation, once it has been read from its file with ``in_file``."""
        return list(self._source)

    @staticmethod
    def by_rule(violations: list[Violation]) -> dict[str, list[Violation]]:
        """violations under the rule each breaks, in the order they come; a violation that names no rule is ``unknown``."""
        grouped: dict[str, list[Violation]] = {}
        for violation in violations:
            grouped.setdefault(violation.rule or "unknown", []).append(violation)
        return grouped

    @property
    def described(self) -> str:
        """The message with what it was found on in front, the way a report lists it."""
        return f"{self.subject}: {self._message}" if self.subject else self._message

    def is_under(self, prefixes: list[str]) -> bool:
        """True when this violation's file is one of the path prefixes or sits under one."""
        location = self.location.replace("\\", "/")
        folders = [prefix.replace("\\", "/").strip("/") for prefix in prefixes if str(prefix).strip()]
        return any(location == folder or location.startswith(f"{folder}/") for folder in folders)

    def in_file(self, location: str, file: Path) -> Violation:
        """This violation named from location, with the lines around it read from file; a violation found on a node
        still holds that node's rule."""
        moved = copy.copy(self)
        moved._location = self._location.moved_to(location)
        moved._source = self._lines_around(file)
        return moved

    def _lines_around(self, file: Path) -> list[SourceLine]:
        line = self.line
        if not line or not file.is_file():
            return []
        lines = file.read_text(encoding="utf-8", errors="replace").split("\n")
        first = max(1, line - QUOTED_LINES_BEFORE)
        return [SourceLine(number, text.rstrip("\r")) for number, text in enumerate(lines[first - 1 : line + QUOTED_LINES_AFTER], first)]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Violation) and self._identity == other._identity

    def __hash__(self) -> int:
        return hash(self._identity)

    @property
    def _identity(self) -> tuple:
        return (self.practice, self.rule, self.node_id, self._message, self.location, self.line, self.end_line)

    def __repr__(self) -> str:
        return f"Violation({self.rule!r}, {self.described!r} at {self.location}:{self.line})"


class Finding:
    """One thing a rule's check found: the node it found it on, what it says, and the lines it is on when they are not
    the node's own, such as a module helper only one class uses, which a class rule finds on the class but is on the
    helper's own lines. A viewer marks those lines."""

    def __init__(self, node: Node, message: str, lines: tuple[int, int] | None = None) -> None:
        self.node = node
        self.message = message
        self.lines = lines

    def __repr__(self) -> str:
        return f"Finding({self.node.name!r}, {self.message!r})"


class NodeViolation(Violation):
    """A rule broken on a graph node: it holds the node's rule that found it (a *GraphRule*), and through that rule the
    node and its practice, so its rule, practice, node, and subject are theirs, not copies. A saved graph keeps it as
    the same data as any violation, which names them by slug, key, and id."""

    def __init__(self, found_by: GraphRule, message: str, location: Location = NOWHERE) -> None:
        super().__init__(FoundBy(""), message, location)
        self.found_by = found_by

    @classmethod
    def at_node(cls, found_by: GraphRule, finding: Finding) -> NodeViolation:
        """A violation the rule found_by found on its node, on the lines finding names, else at the node's place in its
        file."""
        source = found_by.node.source
        start, end = finding.lines if finding.lines is not None else (source.start_line, source.end_line)
        return cls(found_by, finding.message, Location(source.file or "", start, end))

    @property
    @data_field
    def rule(self) -> str:
        return self.found_by.slug

    @property
    @data_field
    def practice(self) -> str:
        return self.found_by.node.practice.key

    @property
    @data_field
    def node_id(self) -> str:
        return self.found_by.node.node_id

    @property
    @data_field
    def subject(self) -> str:
        node = self.found_by.node
        return f"{node.type} `{node.name}`"
