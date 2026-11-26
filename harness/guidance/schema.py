"""One practice ``model/schema.yaml`` (or an overlay's ``rules.yaml``), read into its types.

The files are not strict YAML: a schema opens with a bare ``[epic]`` line naming its top
collection, and a field value may be a ``[a | b]`` list. This class is the one reader of that
format, so the graph's edges, rules, and fidelities all see the same types and fields.

A type is a key alone on its line, at the top level (``epic:``) or listed under the type that
owns it (``  - entityRoot:``). Every other ``name: value`` line under it is a field of that type,
written plain (``  uses?: [module]``) or listed (``  - root: entityRoot``). The ``rules:`` and
``where:`` blocks under a type hold its rule slugs and its constraints, not fields.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

_TOP_TYPE = re.compile(r"^([A-Za-z]\w*):\s*$")
_LISTED_TYPE = re.compile(r"^\s+-\s+([A-Za-z]\w*):\s*$")
_FIELD = re.compile(r"^(\s+)(?:-\s+)?([A-Za-z]\w*)(\??):\s*(.*?)\s*$")
_BULLET = re.compile(r"^\s+-\s+(\S+)\s*$")
_BLOCKS = {"rules", "where"}
# A reference to another schema type: a key of the same schema (``route``) or ``practice.type`` (``ddd.entityRoot``).
_REFERENCE = re.compile(r"^[A-Za-z]\w*(?:\.[A-Za-z]\w*)?$")
# Fields that describe the type itself rather than relate it to another type.
_DESCRIBING = frozenset({"is", "fidelity", "path", "name"})
# The back-edge every child list records to its owner: a relationship, but none a node is required to have.
_BACK_EDGE = "belongsTo"
# Field values that name a value type rather than another schema type.
VALUE_TYPES = frozenset({"string", "number", "dotPath"})
# A word of a field's value, which names a type unless it is a value type.
_WORD = re.compile(r"[A-Za-z]\w*")


@dataclass(frozen=True)
class SchemaRelationship:
    """One field of a schema type that relates a node of the type to others: its name, its value as written, and
    whether it is written optional (``name?:``). The graph's edges, its required relationships, and a pattern's added
    edge kinds all read the fields of a type through these."""

    name: str
    written: str
    optional: bool

    @property
    def targets(self) -> tuple[str, ...]:
        """Each word of the value that names a type, value types left out; none for a quoted value. ``ddd.entityRoot``
        names ``ddd`` and ``entityRoot``."""
        if '"' in self.written:
            return ()
        return tuple(word for word in _WORD.findall(self.written.strip()) if word not in VALUE_TYPES)

    @property
    def references(self) -> tuple[str, ...]:
        """The schema types the value names, one (``route``), ``practice.type`` (``ddd.entityRoot``), or each of a list
        (``[a | b]``); none when any part of it is a value type, a quoted value, or no type."""
        parts = tuple(part.strip() for part in self.written.strip().strip("[]").split("|"))
        if not self.written.strip() or any(part in VALUE_TYPES or not _REFERENCE.match(part) for part in parts):
            return ()
        return parts

    @property
    def is_required(self) -> bool:
        """Whether a node of the type must have it: written not optional, naming only other schema types, and not the
        back-edge of a child list. A field a value such as a string satisfies is no relationship to require."""
        return not self.optional and self.name != _BACK_EDGE and bool(self.references)


class SchemaType:
    """One type a schema declares: its fields in the order written, which of them are optional (written ``name?:``),
    the relationships among them (every field with a value that does not describe the type itself), and its rule
    slugs."""

    def __init__(self, key: str) -> None:
        self.key = key
        self.fields: list[tuple[str, str]] = []
        self.optional: set[str] = set()
        self.relationships: list[SchemaRelationship] = []
        self.rules: list[str] = []

    def field(self, name: str) -> str:
        """The first value written for ``name``; empty when the type does not name it."""
        return next((value for field, value in self.fields if field == name), "")

    def add_field(self, name: str, value: str, optional: bool) -> None:
        """Add the field written ``name: value`` (``name?:`` when optional), and the relationship it is when it has a
        value that does not describe the type itself."""
        self.fields.append((name, value))
        if optional:
            self.optional.add(name)
        if value and name not in _DESCRIBING:
            self.relationships.append(SchemaRelationship(name, value, optional))

    @property
    def required_relationships(self) -> dict[str, tuple[str, ...]]:
        """Each relationship a node of this type must have (``SchemaRelationship.is_required``), with the types it may
        lead to (``route`` or ``ddd.entityRoot``); the first written when one is written twice."""
        found: dict[str, tuple[str, ...]] = {}
        for relationship in self.relationships:
            if relationship.is_required:
                found.setdefault(relationship.name, relationship.references)
        return found

    @property
    def fidelity(self) -> str:
        """The fidelity that creates this type."""
        return self.field("fidelity")

    @property
    def supertype(self) -> str:
        """The type named on ``is:``: a key in the same schema, a Clean Engineering token, or ``practice.type``."""
        return self.field("is")


class Schema:
    """The types one schema file declares, keyed by their schema key, in the order written, and the file's own text,
    which tells an action the shape its output conforms to. A practice holds the one its ``model/schema.yaml`` holds."""

    # Each schema file read in this process, by its path, so a file is read once however many practices load it.
    _loaded: ClassVar[dict[Path, Schema]] = {}

    def __init__(self, text: str) -> None:
        self.types: dict[str, SchemaType] = {}
        self._read(text)

    @classmethod
    def load(cls, path: Path) -> Schema:
        """The schema at ``path``; an empty schema when there is no file. Each file is read once per process."""
        path = Path(path)
        if path not in cls._loaded:
            cls._loaded[path] = cls(path.read_text(encoding="utf-8") if path.is_file() else "")
        return cls._loaded[path]

    def guide(self) -> str:
        """What tells an action to conform its output to this schema; none for an empty schema."""
        if not self.text:
            return ""
        return f"Guide this action so the output conforms to this schema.\n\n{self.text}"

    def _fidelities(self) -> dict[str, str]:
        """Each type key mapped to the fidelity that creates it, for the types that name one."""
        return {key: kind.fidelity for key, kind in self.types.items() if kind.fidelity}

    def node_fidelities(self, order: list[str]) -> dict[str, list[str]]:
        """Each type key with the fidelity that creates it and every one after it in order, the fidelities of the
        practice from lowest to highest: a node a low fidelity creates also belongs to the higher ones, which build it
        out rather than replace it. A type whose fidelity is not in order is left out."""
        created = self._fidelities()
        return {node: order[order.index(fidelity):] for node, fidelity in created.items() if fidelity in order}


    def rules(self) -> dict[str, tuple[str, ...]]:
        """Each type key mapped to the rule slugs its ``rules:`` block lists, for the types that have one."""
        return {key: tuple(kind.rules) for key, kind in self.types.items() if kind.rules}

    def _read(self, text: str) -> None:
        """Read text into its types, keeping the text itself, which tells an action the shape to conform to."""
        self.text = text.strip()
        current: SchemaType | None = None
        block = ""
        block_indent = -1
        for line in text.splitlines():
            header = _TOP_TYPE.match(line) or _LISTED_TYPE.match(line)
            if header and header.group(1) not in _BLOCKS:
                current = self.types.setdefault(header.group(1), SchemaType(header.group(1)))
                block = ""
                continue
            if current is None or not line.strip() or line.lstrip().startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            if block and indent > block_indent:
                self._read_block_item(current, block, line)
                continue
            block = self._read_field(current, line)
            block_indent = indent

    def _read_field(self, current: SchemaType, line: str) -> str:
        """Read one ``name: value`` line of current into its fields; the name of the ``rules:`` or ``where:`` block the
        line opens, else none."""
        field = _FIELD.match(line)
        if field is None:
            return ""
        name, value = field.group(2), field.group(4)
        if name in _BLOCKS and not value:
            return name
        current.add_field(name, value, bool(field.group(3)))
        return ""

    def _read_block_item(self, current: SchemaType, block: str, line: str) -> None:
        bullet = _BULLET.match(line)
        if block == "rules" and bullet is not None and bullet.group(1) not in current.rules:
            current.rules.append(bullet.group(1))
