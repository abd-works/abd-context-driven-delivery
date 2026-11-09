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
from functools import lru_cache
from pathlib import Path

_TOP_TYPE = re.compile(r"^([A-Za-z]\w*):\s*$")
_LISTED_TYPE = re.compile(r"^\s+-\s+([A-Za-z]\w*):\s*$")
_FIELD = re.compile(r"^(\s+)(?:-\s+)?([A-Za-z]\w*)\??:\s*(.*?)\s*$")
_BULLET = re.compile(r"^\s+-\s+(\S+)\s*$")
_BLOCKS = {"rules", "where"}


class SchemaType:
    """One type a schema declares: its fields in the order written, and its rule slugs."""

    def __init__(self, key: str) -> None:
        self.key = key
        self.fields: list[tuple[str, str]] = []
        self.rules: list[str] = []

    def field(self, name: str) -> str:
        """The first value written for ``name``; empty when the type does not name it."""
        return next((value for field, value in self.fields if field == name), "")

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

    def __init__(self, text: str) -> None:
        self.types: dict[str, SchemaType] = {}
        self._read(text)

    @classmethod
    def load(cls, path: Path) -> "Schema":
        """The schema at ``path``; an empty schema when there is no file. Each file is read once per process."""
        return _loaded(Path(path))

    def guide(self) -> str:
        """What tells an action to conform its output to this schema; none for an empty schema."""
        if not self.text:
            return ""
        return f"Guide this action so the output conforms to this schema.\n\n{self.text}"

    def fidelities(self) -> dict[str, str]:
        """Each type key mapped to the fidelity that creates it, for the types that name one."""
        return {key: kind.fidelity for key, kind in self.types.items() if kind.fidelity}

    def node_fidelities(self, order: list[str]) -> dict[str, list[str]]:
        """Each type key with the fidelity that creates it and every one after it in order, the fidelities of the
        practice from lowest to highest: a node a low fidelity creates also belongs to the higher ones, which build it
        out rather than replace it. A type whose fidelity is not in order is left out."""
        created = self.fidelities()
        return {node: order[order.index(fidelity):] for node, fidelity in created.items() if fidelity in order}

    def fidelity_errors(self, declared: list[str]) -> list[str]:
        """What is wrong between this schema and declared, the fidelities of its practice: a schema with no node
        fidelity, or a node fidelity that is none of them. Empty when they agree."""
        created = self.fidelities()
        if not created:
            return ["schema defines no node fidelity entries"]
        known = sorted(declared)
        return [
            f"{node} maps to fidelity {fidelity!r}, which is not under ## Fidelities (have {known!r})"
            for node, fidelity in sorted(created.items()) if fidelity not in known
        ]

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
            block = ""
            field = _FIELD.match(line)
            if field is None:
                continue
            name, value = field.group(2), field.group(3)
            if name in _BLOCKS and not value:
                block, block_indent = name, indent
                continue
            current.fields.append((name, value))

    def _read_block_item(self, current: SchemaType, block: str, line: str) -> None:
        bullet = _BULLET.match(line)
        if block == "rules" and bullet is not None and bullet.group(1) not in current.rules:
            current.rules.append(bullet.group(1))


@lru_cache(maxsize=None)
def _loaded(path: Path) -> Schema:
    return Schema(path.read_text(encoding="utf-8") if path.is_file() else "")
