"""A class's stereotypes as code carries them, such as DDD's Aggregate Root or Value Object.

A stereotype is a UML mark on a class, written `<<Aggregate Root>>` in a model. Code carries it as a decorator with no
arguments (`@aggregate_root` in Python, `@AggregateRoot()` in TypeScript), as a `<<Mark>>` at the start of the class's
doc comment, or as a `<<Mark>>` in a comment line just above the class. The class model holds each one as plain words,
`Aggregate Root`, so every language reads and writes the same stereotypes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from cdd_guidance.practices.clean_engineering.model.field_types import Relationship

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass

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


# The doc comment line that names the modules a class is kept in, outermost first: `Module: Sales | custom · Cart`.
MODULE_LINE = "Module:"
_MODULE_PATH = " · "


def joined_module_path(labels: List[str]) -> str:
    """A module path as one name: its labels, outermost first, joined by ` · `."""
    return _MODULE_PATH.join(labels)


def module_path_in(text: str) -> List[str]:
    """The labels a module path written as one name holds: `Customer | custom · Customer Profile`."""
    return [part.strip() for part in text.split(_MODULE_PATH.strip()) if part.strip()]


def marked_intent(stereotypes: List[str], intent: str) -> str:
    """The intent with the stereotypes written as `<<Mark>>`s at the start of its first line."""
    marks = " ".join(f"<<{item}>>" for item in stereotypes)
    return f"{marks} {intent}".strip() if marks else intent


class DocComment:
    """<<Value Object>> A class's doc comment as written: the module path its `Module:` line names, the stereotypes its
    first line marks, the intent the rest of it says, and the dependencies it lists last, each a `---<<label>>-->
    Target` line with its details under it. Code has no other place for where a class is kept apart from its file, or
    for the facts a dependency names beside its label. It holds the comment's text, reads what it says into a class,
    and is written from one."""

    def __init__(self, text: str = "") -> None:
        self._lines = text.strip().splitlines()

    def text(self) -> str:
        return "\n".join(self._lines)

    @property
    def stereotypes(self) -> List[str]:
        """The stereotypes the comment's first line marks."""
        return marks_in(self._said().partition("\n")[0])

    def describe(self, oclass: "OoadClass") -> None:
        """Give oclass what the comment says beside its stereotypes: its intent, its module path, and its
        dependencies."""
        said = self._said()
        first, _, rest = said.partition("\n")
        oclass.intent = "\n".join(part for part in (without_marks(first), rest.strip()) if part) if marks_in(first) else said
        oclass.module_path = self._module_path()
        oclass.dependencies = Relationship.split_off(self._after_module_line())[1]

    def _said(self) -> str:
        """The text between the module path line and the dependencies."""
        return "\n".join(Relationship.split_off(self._after_module_line())[0]).strip()

    def _module_path(self) -> List[str]:
        first = self._lines[0] if self._lines else ""
        return module_path_in(first[len(MODULE_LINE):]) if first.startswith(MODULE_LINE) else []

    def _after_module_line(self) -> List[str]:
        return self._lines[1:] if self._lines and self._lines[0].startswith(MODULE_LINE) else list(self._lines)


@dataclass
class ClassHead:
    """What sits above a class declaration in brace-language source: its doc comment and the stereotypes its decorators
    and comment lines carry. A blank line, or any other code, ends the head."""

    documented: DocComment = field(default_factory=DocComment)
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
        self.documented = DocComment("\n".join(part.strip().lstrip("*").strip() for part in body.splitlines()))
        self.stereotypes[:0] = self.documented.stereotypes
        return start

    def _take_line(self, line: str) -> None:
        bare = _BARE_DECORATOR.match(line)
        if bare:
            self.stereotypes.insert(0, stereotype_named(bare.group(1)))
        elif _IMPLEMENTS_COMMENT.match(line):
            self.implemented[:0] = [name.strip() for name in _IMPLEMENTS_COMMENT.match(line).group(1).split(",") if name.strip()]
        elif not line.startswith("@"):
            self.stereotypes[:0] = marks_in(line)
