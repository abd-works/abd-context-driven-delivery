"""The uses the code writes outside any member: a module's own statements, which run when it is imported (a registry it
registers with, a module variable it builds, a script's start-up, an `if __name__ == "__main__":` block, a class
declared inside an `if`), joined as made by the folder that holds the file; and a class's own statements (its
attributes' initializers and its metaclass), joined as made by the class. Without them a function only an import-time
statement calls, or a class only a class attribute builds, would read as unused."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.reading.code_file import (
    CREATED_WITH_THE_CLASS,
    NAMED_AS_A_VALUE,
    REACHED_FACT,
    THROUGH_FACT,
    CodeSpan,
    SpanReach,
)
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT
from cdd_guidance.practices.clean_engineering.reading.folder_facts import folders_of

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading

# What the members a module's own statements reach are reached through, and a class's own statements.
MODULE_STATEMENTS = "module statements"
CLASS_STATEMENTS = "class statements"
# An import, which names what the module uses but runs none of it: Python's `import x`, `from x import (`, and a
# script's `import ... from '...'` or `export ... from '...'`.
_PYTHON_IMPORT = re.compile(r"^\s*(?:import\s|from\s+\S+\s+import\b)")
_SCRIPT_IMPORT = re.compile(r"^\s*(?:import[\s{*'\"]|export\s*(?:\{|\*)[^;]*\bfrom\b|export\s*\{\s*$)")
# The metaclass a Python class's header names, and every character of a header but its line ends.
_METACLASS = re.compile(r"\bmetaclass\s*=\s*([\w.]+)")
_NOT_A_NEWLINE = re.compile(r"[^\n]")


class StatementLinks:
    """The edges from the statements written outside any member of the code read: each production file's module
    statements as made by the folder that holds it, and each code class's own statements as made by the class."""

    def __init__(self, reading: "GraphReading") -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._index = reading.code_index
        self._test_code = reading.test_code

    def link(self) -> None:
        members = [*self._in_graph.nodes("Operation"), *self._in_graph.nodes("Property")]
        classes = [node for node in self._in_graph.nodes("OoadClass") if node.name != MODULE_FUNCTION_HOLDER and not node.has_fact(DESCRIBED_FACT)]
        held: dict[str, list[tuple[int, int]]] = {}
        for node in [*classes, *(member for member in members if member.get_fact("owner") == MODULE_FUNCTION_HOLDER)]:
            held.setdefault(node.source.file, []).append((node.source.start_line, node.source.end_line))
        folders = sorted(folders_of(self._in_graph), key=lambda folder: -len(folder.source.file or ""))
        # A file that declares nothing, such as a package's `__init__.py`, still has statements: each file whose imports
        # its folder keeps is read too.
        imported = {file for folder in folders for file in (folder.get_fact("imported_classes_by_file") or {})}
        for file in sorted(set(held) | imported):
            if self._is_production(file):
                self._link_module(file, held.get(file, []), folders)
        declared_members: dict[int, list] = {}
        for member in members:
            declared_members.setdefault(id(self._index.class_declaring(member)), []).append(member)
        for declared in classes:
            if self._is_production(declared.source.file):
                self._link_class(declared, declared_members.get(id(declared), []))

    def _link_module(self, file: str, spans: list[tuple[int, int]], folders: "list[Node]") -> None:
        """Join what the file's own statements reach, as made by the nearest folder that holds the file."""
        folder = next((node for node in folders if not node.source.file or file.startswith(f"{node.source.file}/")), None)
        if folder is None:
            return
        code_file = self._index.file(file)
        lines = self._index.answers.text_of(file).split("\n")
        statements = _outside(lines, spans, _SCRIPT_IMPORT if code_file.is_script else _PYTHON_IMPORT)
        self._relate(folder, code_file.reach_of(CodeSpan(CodeSpan.code_of(statements))), MODULE_STATEMENTS)

    def _link_class(self, declared: "Node", members: "list[Node]") -> None:
        """Join what the class's own statements reach, its attributes' initializers built with the class, and its
        metaclass, as made by the class."""
        text = declared.source.text or ""
        header_end = _header_end(text)
        metaclass = _METACLASS.search(text[:header_end])
        code_file = self._index.file(declared.source.file)
        if metaclass is not None:
            named = code_file.class_named(metaclass.group(1).rsplit(".", 1)[-1])
            if named is not None and named is not declared:
                self._graph.edges.relate("dependsOn", declared, named, {REACHED_FACT: [NAMED_AS_A_VALUE], THROUGH_FACT: ["metaclass"]})
        first = declared.source.start_line
        # The header is left out where it stands, so each line keeps its number.
        unheaded = _NOT_A_NEWLINE.sub(" ", text[:header_end]) + text[header_end:]
        spans = [(member.source.start_line - first + 1, member.source.end_line - first + 1) for member in members]
        statements = _outside(unheaded.split("\n"), spans, None)
        span = CodeSpan(CodeSpan.code_of(statements), declared, creates=CREATED_WITH_THE_CLASS)
        self._relate(declared, code_file.reach_of(span), CLASS_STATEMENTS)

    def _relate(self, user: "Node", reach: SpanReach, through: str) -> None:
        """Record that user invokes each member reach found, and depends on each other class it reaches."""
        for member in dict.fromkeys(reach.members):
            self._graph.edges.relate("invokes", user, member)
        for other, how in reach.classes:
            if other is not user:
                self._graph.edges.relate("dependsOn", user, other, {REACHED_FACT: [how], THROUGH_FACT: [through]})

    def _is_production(self, file: str) -> bool:
        return bool(file) and not file.endswith(".md") and not self._test_code.is_example_code(file)


def _outside(lines: list[str], spans: list[tuple[int, int]], imports: "re.Pattern | None") -> str:
    """The lines no span holds, by their numbers from one, and no import, each kept in its place as an empty line when
    left out, so what remains is the statements written outside them."""
    inside = {number for start, end in spans for number in range(start, end + 1)}
    kept: list[str] = []
    # How many brackets an import still holds open, which its next lines close.
    open_in_import = 0
    for number, line in enumerate(lines, start=1):
        starts = imports is not None and imports.match(line) is not None
        if starts or open_in_import > 0:
            open_in_import = max(0, open_in_import + line.count("(") + line.count("{") - line.count(")") - line.count("}"))
            kept.append("")
            continue
        kept.append("" if number in inside else line)
    return "\n".join(kept)


def _header_end(text: str) -> int:
    """Where a class's header ends in its text: after the colon that closes a Python class's line, or the brace that
    opens a script class's body."""
    depth = 0
    for position, character in enumerate(text):
        if character in "([":
            depth += 1
        elif character in ")]":
            depth -= 1
        elif depth == 0 and character in ":{":
            return position + 1
    return len(text)
