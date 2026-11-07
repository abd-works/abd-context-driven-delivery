"""A class's stereotypes as code carries them, such as DDD's Aggregate Root or Value Object.

A stereotype is a UML mark on a class, written `<<Aggregate Root>>` in a model. Code carries it as a decorator with no
arguments (`@aggregate_root` in Python, `@AggregateRoot()` in TypeScript), as a `<<Mark>>` at the start of the class's
doc comment, or as a `<<Mark>>` in a comment line just above the class. The class model holds each one as plain words,
`Aggregate Root`, so every language reads and writes the same stereotypes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

_MARK = re.compile(r"<<\s*([^>]+?)\s*>>")
# A decorator with no arguments is a stereotype; one with arguments configures the class.
_BARE_DECORATOR = re.compile(r"^@([A-Za-z_]\w*)(?:\(\s*\))?$")
_ANY_DECORATOR = re.compile(r"^@[\w.]+")
_IMPLEMENTS_COMMENT = re.compile(r"^//\s*implements\s+(.+)$")
_WORDS = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


def stereotype_named(decorator: str) -> str:
    """The stereotype a decorator name spells: `aggregate_root` and `AggregateRoot` are both `Aggregate Root`."""
    return " ".join(word[:1].upper() + word[1:] for part in decorator.split("_") for word in _WORDS.findall(part))


def snake_case_decorator(stereotype: str) -> str:
    """`Aggregate Root` as Python spells its decorator: `aggregate_root`."""
    return "_".join(word.lower() for word in re.split(r"[\s/_-]+", stereotype) if word)


def pascal_case_decorator(stereotype: str) -> str:
    """`Aggregate Root` as TypeScript spells its decorator: `AggregateRoot`."""
    return "".join(word[:1].upper() + word[1:] for word in re.split(r"[\s/_-]+", stereotype) if word)


def marks_in(text: str) -> List[str]:
    """Each `<<Mark>>` in text, as written."""
    return [item.strip() for item in _MARK.findall(text)]


def without_marks(text: str) -> str:
    return _MARK.sub("", text).strip()


def marked_intent(stereotypes: List[str], intent: str) -> str:
    """The intent with the stereotypes written as `<<Mark>>`s at the start of its first line."""
    marks = " ".join(f"<<{item}>>" for item in stereotypes)
    return f"{marks} {intent}".strip() if marks else intent


@dataclass
class DocumentedIntent:
    """A doc comment read into the stereotypes its first line marks and the intent the rest of it says."""

    stereotypes: List[str] = field(default_factory=list)
    intent: str = ""

    @classmethod
    def read(cls, doc: str) -> "DocumentedIntent":
        first, _, rest = doc.strip().partition("\n")
        marks = marks_in(first)
        if not marks:
            return cls([], doc.strip())
        return cls(marks, "\n".join(part for part in (without_marks(first), rest.strip()) if part))


@dataclass
class ClassHead:
    """What sits above a class declaration in brace-language source: its doc comment and the stereotypes its decorators
    and comment lines carry. A blank line, or any other code, ends the head."""

    doc: str = ""
    stereotypes: List[str] = field(default_factory=list)
    # The bases a `// implements A, B` comment names, for a language with no `implements` of its own.
    implemented: List[str] = field(default_factory=list)

    @classmethod
    def above(cls, text_before_class: str) -> "ClassHead":
        head = cls()
        lines = text_before_class.splitlines()
        index = len(lines) - 1
        while index >= 0:
            line = lines[index].strip()
            if line.endswith("*/") and "/**" in "\n".join(lines[: index + 1]):
                index = head._take_doc(lines, index)
            elif _ANY_DECORATOR.match(line) or line.startswith(("//", "#")):
                head._take_line(line)
            elif line not in ("export", "export default", "abstract"):
                break
            index -= 1
        return head

    def _take_doc(self, lines: List[str], end: int) -> int:
        """Read the doc comment ending on line end; the line it opens on."""
        start = end
        while "/**" not in lines[start]:
            start -= 1
        body = "\n".join(lines[start : end + 1]).split("/**", 1)[1].rsplit("*/", 1)[0]
        documented = DocumentedIntent.read("\n".join(part.strip().lstrip("*").strip() for part in body.splitlines()))
        self.doc = documented.intent
        self.stereotypes[:0] = documented.stereotypes
        return start

    def _take_line(self, line: str) -> None:
        bare = _BARE_DECORATOR.match(line)
        if bare:
            self.stereotypes.insert(0, stereotype_named(bare.group(1)))
        elif _IMPLEMENTS_COMMENT.match(line):
            self.implemented[:0] = [name.strip() for name in _IMPLEMENTS_COMMENT.match(line).group(1).split(",") if name.strip()]
        elif not line.startswith("@"):
            self.stereotypes[:0] = marks_in(line)
