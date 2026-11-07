"""One place a rule is broken. A graph rule records it on the node it checked, the saved graph keeps it, the explorer
shows it under the node's rule, and the validation report and the board read it back from the saved graph."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from harness.installation.destination import SourceFile, data_field

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


class Violation:
    """A rule broken at one place: the rule and the practice that checks it, the node it was found on, what that node
    is (``Operation `checkout```), the file and lines, the message, and how severe it is. A finding that names no node,
    such as a draw.io scanner's or a judged rule's, leaves the node out; one that names no file is at ``unknown``."""

    def __init__(
        self,
        rule: str,
        message: str,
        *,
        practice: str = "",
        node_id: str = "",
        subject: str = "",
        location: str = "",
        line: int | None = None,
        end_line: int | None = None,
        severity: str = "error",
        source: list[SourceLine] | None = None,
    ) -> None:
        self._rule = rule
        self._message = (message or "").strip()
        self._practice = practice
        self._node_id = node_id
        self._subject = subject
        self._location = location or UNKNOWN_LOCATION
        self._line = int(line) if line else None
        self._end_line = int(end_line) if end_line else self._line
        self._severity = severity
        self._source = list(source or [])

    @classmethod
    def on_node(cls, rule: str, message: str, node) -> Violation:
        """A violation of rule found on node, at the node's place in its file."""
        source = node.source
        return cls(
            rule,
            message,
            practice=node.practice.name,
            node_id=node.node_id,
            subject=f"{node.type} `{node.name}`",
            location=source.file or "",
            line=source.start_line,
            end_line=source.end_line,
        )

    @classmethod
    def from_saved(cls, practice: str, saved: list, node_rows: dict[str, list]) -> Violation:
        """A violation as the saved graph keeps it, ``[rule, node_id, message, file, line, end_line, severity]``; the
        node's saved row names what the node is."""
        rule, node_id, message, location, line, end_line, severity = (list(saved) + [""] * 7)[:7]
        row = node_rows.get(node_id) or []
        subject = f"{row[2]} `{row[1]}`" if len(row) > 2 and row[1] else ""
        return cls(
            str(rule),
            str(message),
            practice=practice,
            node_id=str(node_id),
            subject=subject,
            location=str(location or (row[4] if len(row) > 4 else "")),
            line=line or (row[5] if len(row) > 5 else None),
            end_line=end_line or (row[6] if len(row) > 6 else None),
            severity=str(severity or "error"),
        )

    @classmethod
    def from_data(cls, data: dict) -> Violation:
        """A violation sent as data, the way ``data_of`` writes it for ``graph.return_nodes``."""
        return cls(
            str(data.get("rule") or ""),
            str(data.get("message") or ""),
            practice=str(data.get("practice") or ""),
            node_id=str(data.get("node_id") or ""),
            subject=str(data.get("subject") or ""),
            location=str(data.get("location") or ""),
            line=data.get("line"),
            end_line=data.get("end_line"),
            severity=str(data.get("severity") or "error"),
        )

    @property
    def saved(self) -> list:
        """This violation as the saved graph keeps it."""
        return [self._rule, self._node_id, self._message, self._location, self._line, self._end_line, self._severity]

    @property
    @data_field
    def rule(self) -> str:
        return self._rule

    @property
    @data_field
    def practice(self) -> str:
        return self._practice

    @property
    @data_field
    def node_id(self) -> str:
        return self._node_id

    @property
    @data_field
    def subject(self) -> str:
        """What the node the violation was found on is, such as ``Operation `checkout```; empty when it names no node."""
        return self._subject

    @property
    @data_field
    def location(self) -> Annotated[str, SourceFile]:
        return self._location

    @property
    @data_field
    def line(self) -> int | None:
        return self._line

    @property
    @data_field
    def end_line(self) -> int | None:
        return self._end_line

    @property
    @data_field
    def message(self) -> str:
        return self._message

    @property
    @data_field
    def severity(self) -> str:
        return self._severity

    @property
    @data_field
    def source(self) -> list[SourceLine]:
        """The lines around the violation, once it has been read from its file with ``in_file``."""
        return list(self._source)

    @property
    def described(self) -> str:
        """The message with what it was found on in front, the way a report lists it."""
        return f"{self._subject}: {self._message}" if self._subject else self._message

    def is_under(self, prefixes: list[str]) -> bool:
        """True when this violation's file is one of the path prefixes or sits under one."""
        location = self._location.replace("\\", "/")
        folders = [prefix.replace("\\", "/").strip("/") for prefix in prefixes if str(prefix).strip()]
        return any(location == folder or location.startswith(f"{folder}/") for folder in folders)

    def in_file(self, location: str, file: Path, lines_before: int, lines_after: int) -> Violation:
        """This violation named from location, with the lines around it read from file."""
        source = self._lines_around(file, lines_before, lines_after)
        return Violation(
            self._rule,
            self._message,
            practice=self._practice,
            node_id=self._node_id,
            subject=self._subject,
            location=location,
            line=self._line,
            end_line=self._end_line,
            severity=self._severity,
            source=source,
        )

    def _lines_around(self, file: Path, lines_before: int, lines_after: int) -> list[SourceLine]:
        if not self._line or not file.is_file():
            return []
        lines = file.read_text(encoding="utf-8", errors="replace").split("\n")
        first = max(1, self._line - lines_before)
        return [SourceLine(number, text.rstrip("\r")) for number, text in enumerate(lines[first - 1 : self._line + lines_after], first)]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Violation) and self.saved == other.saved and self._practice == other._practice

    def __hash__(self) -> int:
        return hash((self._practice, *self.saved))

    def __repr__(self) -> str:
        return f"Violation({self._rule!r}, {self.described!r} at {self._location}:{self._line})"
