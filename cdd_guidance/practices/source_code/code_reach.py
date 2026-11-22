"""The ways a project reaches code other than by a call or an import, which the project names in its
``.context/config.json`` under ``code_reach``, and the operations and classes they reach in its graph. Every rule that
asks whether code is used reads this one list: a test coverage rule counts what a way reaches as reached, and an unused
code rule counts it as used. A project that names none reaches code only by calls and imports."""
from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from harness.graph.graph import Graph, Node
from harness.graph.skipped_folders import scanned_files
from harness.installation.context_config import ContextConfig

# The section of ``.context/config.json`` that names the ways the project reaches code.
CODE_REACH_SECTION = "code_reach"
_DECORATOR = re.compile(r"^\s*@([\w.]+)")
_NAME = re.compile(r"\b[A-Za-z_]\w*\b")
# The code files a registry call is looked for in.
_CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs"}
# An entry point names an operation as ``file:operation``, the file a pattern such as ``*.py``.
_ENTRY_POINT_SEPARATOR = ":"


class WaysCodeIsReached:
    """The ways one project reaches code besides calls and imports, as its config names them:
    - publishing_decorators: a decorator or annotation that publishes the operation or class it marks for a framework
      to call by name, such as a tool, a command, or a route;
    - registries: a call that registers the classes it lists with a registry or plugin list, such as
      ``CATALOGUE.register``; the framework calls each override such a class makes of its bases;
    - scanned_bases: a base class a framework finds its subclasses by, scanning folders or by reflection; it calls each
      override a subclass makes of it;
    - entry_points: an operation the project's configuration or runtime starts, as ``file:operation``;
    - naming_conventions: a pattern of names a framework finds operations and classes by;
    - generated_adapters: the files whose public classes and operations generated code calls, as patterns."""

    def __init__(self, section: dict[str, Any] | None = None) -> None:
        section = section or {}
        self.publishing_decorators = frozenset(section.get("publishing_decorators") or [])
        self.registries = list(section.get("registries") or [])
        self.scanned_bases = frozenset(section.get("scanned_bases") or [])
        self.entry_points = [str(entry).rsplit(_ENTRY_POINT_SEPARATOR, 1) for entry in section.get("entry_points") or [] if _ENTRY_POINT_SEPARATOR in str(entry)]
        self.naming_conventions = [re.compile(pattern) for pattern in section.get("naming_conventions") or []]
        self.generated_adapters = list(section.get("generated_adapters") or [])

    @classmethod
    def from_project(cls, root: Path | str) -> WaysCodeIsReached:
        """The ways the project at root names in its config; none when it names none."""
        return cls(ContextConfig(root).load().get(CODE_REACH_SECTION))

    def is_entry_point(self, file: str, name: str) -> bool:
        return any(fnmatch(file, pattern) and name == operation for pattern, operation in self.entry_points)

    def follows_a_naming_convention(self, name: str) -> bool:
        return any(pattern.search(name) for pattern in self.naming_conventions)

    def is_generated_adapter(self, file: str) -> bool:
        return any(fnmatch(file, pattern) for pattern in self.generated_adapters)


class CodeReach:
    """What a project's ways reach in its graph (*WaysCodeIsReached*): the operations and the classes a framework, a
    registry, an entry point or generated code calls without a call the graph can follow. It reads the source files the
    graph read for the decorators written on them and for the registry calls in them."""

    def __init__(self, graph: Graph, ways: WaysCodeIsReached) -> None:
        self._graph = graph
        self._ways = ways
        self._root = Path(graph.folder or ".")
        self._texts: dict[str, list[str]] = {}
        self._registered: set[str] | None = None

    @classmethod
    def from_graph(cls, graph: Graph) -> CodeReach:
        """The ways the project whose folder graph read names in its config, as they reach that graph."""
        return cls(graph, WaysCodeIsReached.from_project(graph.folder or "."))

    def operations(self, operations: list[Node]) -> list[Node]:
        """The operations among operations that one of the project's ways reaches."""
        names_by_class: dict[int, set[str]] = {}
        for operation in operations:
            owner = self._graph.edges.direct_parent(operation)
            if owner is not None:
                names_by_class.setdefault(id(owner), set()).add(operation.name)
        return [operation for operation in operations if self._reaches_operation(operation, names_by_class)]

    def classes(self, classes: list[Node]) -> list[Node]:
        """The classes among classes that one of the project's ways reaches."""
        return [declared for declared in classes if self._reaches_class(declared)]

    def _reaches_operation(self, operation: Node, names_by_class: dict[int, set[str]]) -> bool:
        file = self._file_of(operation)
        ways = self._ways
        if ways.is_entry_point(file, operation.name) or ways.follows_a_naming_convention(operation.name):
            return True
        if ways.is_generated_adapter(file) and not operation.name.startswith("_"):
            return True
        return self._is_published(operation) or self._overrides_for_a_framework(operation, names_by_class)

    def _reaches_class(self, declared: Node) -> bool:
        ways = self._ways
        if ways.is_generated_adapter(self._file_of(declared)) or ways.follows_a_naming_convention(declared.name):
            return True
        return self._is_published(declared) or self._is_registered(declared)

    def _is_published(self, node: Node) -> bool:
        return bool(self._ways.publishing_decorators & self._decorators_of(node))

    def _is_registered(self, declared: Node) -> bool:
        """Whether a registry lists the class, or a framework finds it by a base it reaches."""
        return declared.name in self._registered_names() or any(base.name in self._ways.scanned_bases for base in self._base_chain(declared))

    def _overrides_for_a_framework(self, operation: Node, names_by_class: dict[int, set[str]]) -> bool:
        """Whether operation overrides an operation of a base, on a class a framework calls through that base."""
        owner = self._graph.edges.direct_parent(operation)
        if owner is None or not self._is_registered(owner):
            return False
        return any(operation.name in names_by_class.get(id(base), set()) for base in self._base_chain(owner))

    def _decorators_of(self, node: Node) -> set[str]:
        """The names of the decorators written just above the node's opening line, and on and after it when the reading
        opens the node at its first decorator."""
        lines = self._lines_of(self._file_of(node))
        line = (node.source.start_line or 0) - 1
        if not 0 <= line < len(lines):
            return set()
        return self._decorator_run(lines, line - 1, -1) | self._decorator_run(lines, line, 1)

    def _decorator_run(self, lines: list[str], index: int, step: int) -> set[str]:
        """The decorators on consecutive lines from index, going up (step -1) or down (step 1)."""
        found = set()
        while 0 <= index < len(lines) and _DECORATOR.match(lines[index]):
            found.add(_DECORATOR.match(lines[index]).group(1).rsplit(".", 1)[-1])
            index += step
        return found

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
        """Each name a registry call lists, in the project's code files; read once, and only when the project names a
        registry."""
        if self._registered is None:
            calls = [re.compile(rf"(?<![\w.]){re.escape(registry)}\(([^()]*)\)") for registry in self._ways.registries]
            files = scanned_files(self._root, _CODE_SUFFIXES) if calls else []
            texts = [path.read_text(encoding="utf-8", errors="replace") for path in files]
            self._registered = {name for text in texts for call in calls for listed in call.findall(text) for name in _NAME.findall(listed)}
        return self._registered

    def _file_of(self, node: Node) -> str:
        return (node.source.file or "").replace("\\", "/")

    def _lines_of(self, file: str) -> list[str]:
        if file not in self._texts:
            path = self._root / file
            self._texts[file] = path.read_text(encoding="utf-8", errors="replace").splitlines() if file and path.is_file() else []
        return self._texts[file]
