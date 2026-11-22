"""The operations the framework calls by a name, a decorator or a registration, never through a call the graph can
follow from a test. TDD's coverage counts each as reached, since a test of the framework call that runs it reaches it."""
from __future__ import annotations

import re
from pathlib import Path

from harness.graph.graph import Graph, Node

# The annotations that publish an operation for the framework to call by name: an MCP tool or toolset operation,
# agent instructions, a skill, a command, rules, and a hook.
_PUBLISHING = frozenset({"mcp", "agent_tool", "agent_instructions", "skill", "command", "rules", "hook"})
_DECORATOR = re.compile(r"^\s*@([\w.]+)")
# A registration with a catalogue, such as ``PRACTICE_CATALOGUE.register(Stories, Ddd)``, and the names it lists.
_REGISTRATION = re.compile(r"\.register\(([^()]*)\)")
_NAME = re.compile(r"\b[A-Za-z_]\w*\b")
# The ending of the base every graph rule reaches, whose check the rule registry runs.
_GRAPH_RULE_ENDING = "GraphRule"


class CalledByName:
    """Among a graph's operations, those the framework calls by name: one published by an annotation (``@mcp``,
    ``@agent_tool``, ``@hook``, and the like), and one that overrides an operation of a base, on a class the framework
    calls through that base: a graph rule, whose check the rule registry runs, and a class registered with a catalogue."""

    def __init__(self, graph: Graph, operations: list[Node]) -> None:
        self._graph = graph
        self._operations = operations
        self._root = Path(graph.folder or ".")
        self._texts: dict[str, list[str]] = {}
        self._names_by_class: dict[int, set[str]] = {}
        for operation in operations:
            owner = graph.edges.direct_parent(operation)
            if owner is not None:
                self._names_by_class.setdefault(id(owner), set()).add(operation.name)
        self._registered = self._registered_names()

    def operations(self) -> list[Node]:
        return [operation for operation in self._operations if self._is_published(operation) or self._overrides_for_the_framework(operation)]

    def _is_published(self, operation: Node) -> bool:
        return bool(_PUBLISHING & self._decorators_of(operation))

    def _decorators_of(self, operation: Node) -> set[str]:
        """The names of the decorators written just above the operation's opening line, and on and after it when the
        reading opens the operation at its first decorator."""
        lines = self._lines_of(operation.source.file or "")
        line = (operation.source.start_line or 0) - 1
        if not 0 <= line < len(lines):
            return set()
        above = self._decorator_run(lines, line - 1, -1)
        return above | self._decorator_run(lines, line, 1)

    def _decorator_run(self, lines: list[str], index: int, step: int) -> set[str]:
        """The decorators on consecutive lines from index, going up (step -1) or down (step 1)."""
        found = set()
        while 0 <= index < len(lines) and _DECORATOR.match(lines[index]):
            found.add(_DECORATOR.match(lines[index]).group(1).rsplit(".", 1)[-1])
            index += step
        return found

    def _overrides_for_the_framework(self, operation: Node) -> bool:
        owner = self._graph.edges.direct_parent(operation)
        if owner is None:
            return False
        bases = self._base_chain(owner)
        if not (owner.name in self._registered or any(base.name.endswith(_GRAPH_RULE_ENDING) for base in bases)):
            return False
        return any(operation.name in self._names_by_class.get(id(base), set()) for base in bases)

    def _base_chain(self, declared: Node) -> list[Node]:
        """Every base class of declared the graph holds, nearest first."""
        chain: list[Node] = []
        waiting = [declared]
        while waiting:
            for edge in self._graph.edges.from_parent("baseClass", waiting.pop()):
                if all(edge.child is not known for known in chain) and edge.child is not declared:
                    chain.append(edge.child)
                    waiting.append(edge.child)
        return chain

    def _registered_names(self) -> set[str]:
        """Each name a registration with a catalogue lists, in the files the operations come from."""
        files = {operation.source.file for operation in self._operations if operation.source.file}
        return {name for file in files for listed in _REGISTRATION.findall("\n".join(self._lines_of(file))) for name in _NAME.findall(listed)}

    def _lines_of(self, file: str) -> list[str]:
        if file not in self._texts:
            path = self._root / file
            self._texts[file] = path.read_text(encoding="utf-8", errors="replace").splitlines() if file and path.is_file() else []
        return self._texts[file]
