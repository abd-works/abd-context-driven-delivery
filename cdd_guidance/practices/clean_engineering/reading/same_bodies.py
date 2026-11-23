"""Operations in different files that do the same work: bodies that are the same statements once the names each body
gives its own values are set aside. A copy whose author renamed every local is still the same behaviour written twice,
which an exact match of the text misses."""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.reading.folder_facts import record_fact
from cdd_guidance.practices.clean_engineering.reading.operation_facts import code_operations, file_qualified_name
from cdd_guidance.practices.clean_engineering.measures.read_facts import parameters_of

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

# The fact each operation of a group keeps: its statements, and every operation of the group, `file: Class.operation`.
SAME_BODY_ELSEWHERE = "same_body_elsewhere"
# A body of one statement is one expression, such as a getter, which reads alike everywhere; it is never compared.
_FEWEST_STATEMENTS_COMPARED = 2
_TOKEN = re.compile(r"[A-Za-z_$][\w$]*|\d+|\S")
_COMMENT_LINE = re.compile(r"^\s*(#|//).*$", re.M)
_DOCSTRING = re.compile(r'"""[\s\S]*?"""|' + r"'''[\s\S]*?'''")
# The names a body gives its own values: an assignment's targets, a loop's, a `with ... as`, an `except ... as`, and a
# script's `const`, `let`, or `var`.
_ASSIGNED = re.compile(r"^\s*([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*(?::[^=\n]+)?(?:[-+*/%|&]|//)?=(?!=)", re.M)
_LOOPED = re.compile(r"\bfor\s+\(?\s*(?:const|let|var)?\s*([\w\s,]+?)\)?\s+(?:in|of)\b")
_NAMED_AS = re.compile(r"\bas\s+([A-Za-z_]\w*)")
_DECLARED = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)")
# The names an object calls itself by, which every method shares.
_OWN_NAMES = frozenset({"self", "cls", "this"})


class SameBodies:
    """The production operations of the graph, grouped by their bodies with each body's own names set aside; each
    operation of a group whose operations sit in more than one file keeps the group (``same_body_elsewhere``). A group
    one of whose operations is already kept as a copy (``duplicate_of``, ``near_copy_of``) is left out, as that copy is
    reported already."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._operations = code_operations(in_graph)

    def record(self) -> None:
        kept: dict[str, list] = {}
        for statements, members in self._groups().values():
            if len({member.source.file for member in members}) > 1 and not any(self._reported_copy(member) for member in members):
                labels = sorted(file_qualified_name(member) for member in members)
                kept.update({member.node_id: [statements, labels] for member in members})
        for operation in self._operations:
            record_fact(operation, SAME_BODY_ELSEWHERE, kept.get(operation.node_id, []))

    def _groups(self) -> dict[str, tuple[int, list["Node"]]]:
        """The operations of two or more statements by the shape of their bodies, each shape with its statements."""
        groups: dict[str, tuple[int, list["Node"]]] = {}
        for operation in self._operations:
            code = self._code(operation)
            statements = sum(1 for line in code.splitlines() if line.strip())
            if statements >= _FEWEST_STATEMENTS_COMPARED:
                groups.setdefault(self._shape(operation, code), (statements, []))[1].append(operation)
        return groups

    def _reported_copy(self, operation: "Node") -> bool:
        """True for an operation already kept as a copy of another, exactly or nearly (``BodyCopies``), which the
        duplication rule reports on its own."""
        return bool(operation.get_fact("duplicate_of") or operation.get_fact("near_copy_of"))

    def _code(self, operation: "Node") -> str:
        """The body's statements, its doc comment and comment lines left out."""
        return _COMMENT_LINE.sub("", _DOCSTRING.sub("", str(operation.get_fact("body_text") or "")))

    def _shape(self, operation: "Node", code: str) -> str:
        """The body's tokens, each of its own names, its parameters' and its locals', as one placeholder; a member it
        reads off another object keeps its name, since that is what the body does."""
        own = self._own_names(operation, code)
        tokens = _TOKEN.findall(code)
        shaped = [
            "_" if token in own and (index == 0 or tokens[index - 1] != ".") else token
            for index, token in enumerate(tokens)
        ]
        return hashlib.sha1(" ".join(shaped).encode("utf-8")).hexdigest()

    def _own_names(self, operation: "Node", code: str) -> set[str]:
        names = {parameter.name for parameter in parameters_of(operation)}
        for pattern in (_ASSIGNED, _LOOPED, _NAMED_AS, _DECLARED):
            for found in pattern.finditer(code):
                names.update(name.strip() for name in found.group(1).split(",") if name.strip())
        return names - _OWN_NAMES
