"""A relationship from one class to another. On a property its kind is composition, aggregation, or association, with a
cardinality of 0..1, 0..*, 1, or 1..*. A class's dependency has the kind dependency and a label that names the
interaction, such as `runs` or `reads sections with`, drawn as `Repo ---<<runs>>--> Git`."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# How strongly each kind of relationship binds its classes: where two are drawn between the same classes, the stronger
# one stands.
RELATIONSHIP_STRENGTH = {"inheritance": 4, "composition": 3, "aggregation": 2, "association": 1, "relative": 1, "dependency": 0}
# A dependency line: `---<<reads sections with>>--> MarkdownText`.
_DEPENDENCY_LINE = re.compile(r"^\s*-{3}<<\s*(?P<label>.+?)\s*>>-{2}>\s*(?P<target>[A-Za-z_][\w.]*)\s*$")
# A fact written under a dependency line: `direction: downstream`.
_DETAIL_LINE = re.compile(r"^\s*(?P<key>[A-Za-z][\w ]*?)\s*:\s*(?P<value>.*?)\s*$")


@dataclass
class Relationship:
    target: str
    kind: str = ""
    cardinality: str = ""
    description: str = ""
    sequential_order: int = 0
    label: str = ""
    # The facts a dependency's source names beside its label, in the order it names them, such as the direction and
    # the pattern of an integration between two parts of a domain. Most dependencies name none.
    details: Dict[str, str] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.target

    @classmethod
    def read_line(cls, line: str) -> Optional["Relationship"]:
        """The dependency a `---<<label>>--> Target` line names; none for any other line."""
        found = _DEPENDENCY_LINE.match(line)
        if found is None:
            return None
        return cls(target=found.group("target"), kind="dependency", label=found.group("label"))

    @classmethod
    def split_off(cls, lines: List[str]) -> tuple[List[str], List["Relationship"]]:
        """A description's text lines, and the dependencies the lines after them write, from the first dependency line
        on: a class card's body and a doc comment both end with them."""
        first = next((index for index, line in enumerate(lines) if cls.read_line(line)), len(lines))
        return lines[:first], cls.read_lines(lines[first:])

    @classmethod
    def read_lines(cls, lines: List[str]) -> List["Relationship"]:
        """The dependencies the lines write: each dependency line opens one, and the `key: value` lines under it are
        its details."""
        found: List[Relationship] = []
        for line in lines:
            opened = cls.read_line(line)
            if opened is not None:
                found.append(opened)
            elif found and _DETAIL_LINE.match(line):
                detail = _DETAIL_LINE.match(line)
                found[-1].details[detail.group("key")] = detail.group("value")
        return found

    def line(self) -> str:
        """The dependency as one line: `---<<label>>--> Target`."""
        return f"---<<{self.label}>>--> {self.target}"

    def lines(self) -> List[str]:
        """The dependency line, then a `key: value` line for each of its details."""
        return [self.line()] + [f"  {key}: {value}" for key, value in self.details.items()]

    def as_record(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "kind": self.kind,
            "cardinality": self.cardinality,
            "description": self.description,
            "label": self.label,
            "details": dict(self.details),
        }

    def translate_from(self, source: "Relationship") -> None:
        self.update_self(source)

    def update_self(self, source: "Relationship") -> None:
        self.target = source.target
        self.kind = source.kind
        self.cardinality = source.cardinality
        self.description = source.description
        self.sequential_order = source.sequential_order
        self.label = source.label
        self.details = dict(source.details)

    def clone(self) -> "Relationship":
        return type(self)(
            target=self.target,
            kind=self.kind,
            cardinality=self.cardinality,
            description=self.description,
            sequential_order=self.sequential_order,
            label=self.label,
            details=dict(self.details),
        )
