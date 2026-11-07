"""The seam a practice or a pattern overlay fills to take part in the graph.

The graph names no practice. A practice gives the graph a *GraphPractice*: how it reads a working copy into its
practice graph, how it links its nodes to other practices' nodes once every practice is read, and the rules it checks.
A pattern gives a *GraphOverlay*: the nodes it adds on top of the practices and the rules it adds to each. Each one
registers itself from its own ``graph_practice`` (or ``graph_overlay``) module, which the graph imports the first time
it asks for that practice or pattern, so the practices depend on the graph and never the other way round.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from harness.graph.language_for_node import language_for_node
from harness.graph.practice_rule import PracticeGraphRule

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node, PracticeGraph

# Languages a node's file can be in whose rules every practice already checks; any other names a channel.
_CODE_LANGUAGES = frozenset({"graph", "python", "typescript", "javascript"})
_PATTERNS_PACKAGE = "cdd_guidance.patterns"


def rules_in(module_path: str) -> dict[str, PracticeGraphRule]:
    """The rules a rules module lists, by slug: its ``BY_SLUG``, else each of its ``RULES``. A module that is not there
    has none."""
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as missing:
        if missing.name and module_path.startswith(missing.name):
            return {}
        raise
    by_slug = getattr(module, "BY_SLUG", None)
    if isinstance(by_slug, dict):
        return dict(by_slug)
    return {rule.slug: rule for rule in getattr(module, "RULES", ()) if getattr(rule, "slug", "")}


class GraphPractice:
    """What one practice gives the graph. The base reads nothing and checks the rules in its practice's ``rules``
    package, so a practice that only checks rules needs no subclass."""

    def __init__(self, name: str, package: str = "") -> None:
        self.name = name
        self.package = package
        self._rules: dict[str, PracticeGraphRule] | None = None

    reads_after: tuple[str, ...] = ()
    """The practices whose nodes this one reads while it reads its own; the graph reads them first."""

    node_types: tuple[str, ...] = ()
    """Node types the explorer offers for this practice even before any node of them is read."""

    def read(self, practice: PracticeGraph) -> None:
        """Read this practice's nodes and edges from the working copy ``practice.graph`` is loading."""

    def link(self, graph: Graph) -> None:
        """Record the edges between this practice's nodes and other practices' nodes, once every practice is read."""

    def rules(self) -> dict[str, PracticeGraphRule]:
        """Every rule this practice checks, by slug."""
        if self._rules is None:
            self._rules = self.own_rules()
        return self._rules

    def own_rules(self) -> dict[str, PracticeGraphRule]:
        return rules_in(f"{self.package}.rules") if self.package else {}

    def language_rules(self, language: str) -> dict[str, PracticeGraphRule]:
        """The rules this practice checks only on nodes read from a file in ``language``, such as ``drawio``."""
        return {}

    def checks(self, patterns: tuple[str, ...] = ()) -> dict[str, PracticeGraphRule]:
        """This practice's rules with those each active pattern adds to it."""
        merged = dict(self.rules())
        for pattern in patterns:
            merged.update(GraphPractices.overlay(pattern).rules_for(self.name))
        return merged

    def checks_for(self, node: Node, patterns: tuple[str, ...]) -> dict[str, PracticeGraphRule]:
        """The checks that apply to node: its type's, or the Clean Engineering type a pattern anchors it to."""
        from harness.graph.schema_rules import ce_anchor_type

        merged = self.checks(patterns)
        language = language_for_node(node)
        if language and language not in _CODE_LANGUAGES:
            merged.update(self.language_rules(language))
        types = {node.type}
        anchor = ce_anchor_type(self.name, node.type, patterns)
        if anchor:
            types.add(anchor)
        return {slug: rule for slug, rule in merged.items() if any(rule.applies_to(type_name) for type_name in types)}


class GraphOverlay:
    """What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each
    practice, which live in ``<pattern>/practices/<practice>/rules``."""

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    def read(self, graph: Graph) -> None:
        """Add this pattern's nodes and edges to the practices ``graph`` holds."""

    def guidance(self):
        """The pattern's guidance, whose rules give each of its graph rules its prose; none when it has no guidance."""
        return None

    def rules_for(self, practice: str) -> dict[str, PracticeGraphRule]:
        return rules_in(f"{_PATTERNS_PACKAGE}.{self.pattern}.practices.{practice}.rules")


class GraphPractices:
    """Every practice and pattern overlay registered with the graph."""

    _practices: dict[str, GraphPractice] = {}
    _overlays: dict[str, GraphOverlay] = {}

    @classmethod
    def register(cls, practice: GraphPractice) -> None:
        cls._practices[practice.name] = practice

    @classmethod
    def register_overlay(cls, overlay: GraphOverlay) -> None:
        cls._overlays[overlay.pattern] = overlay

    @classmethod
    def named(cls, name: str) -> GraphPractice:
        """The practice called name. A practice that registers nothing still checks its rules package."""
        if name not in cls._practices:
            cls._discover(name)
        return cls._practices[name]

    @classmethod
    def overlay(cls, pattern: str) -> GraphOverlay:
        if pattern not in cls._overlays:
            cls._import(f"{_PATTERNS_PACKAGE}.{pattern}.graph_overlay")
            cls._overlays.setdefault(pattern, GraphOverlay(pattern))
        return cls._overlays[pattern]

    @classmethod
    def in_reading_order(cls, names: list[str]) -> list[GraphPractice]:
        """The practices called names, each after the practices it reads."""
        ordered: list[GraphPractice] = []
        for name in names:
            cls._place(cls.named(name), names, ordered)
        return ordered

    @classmethod
    def _place(cls, practice: GraphPractice, names: list[str], ordered: list[GraphPractice]) -> None:
        if practice in ordered:
            return
        for earlier in practice.reads_after:
            if earlier in names:
                cls._place(cls.named(earlier), names, ordered)
        ordered.append(practice)

    @classmethod
    def _discover(cls, name: str) -> None:
        from harness.guidance.practice_catalogue import PracticeCatalogue

        package = PracticeCatalogue.module_of(name) if PracticeCatalogue.has(name) else ""
        if package:
            cls._import(f"{package}.graph_practice")
        cls._practices.setdefault(name, GraphPractice(name, package))

    @classmethod
    def _import(cls, module_path: str) -> None:
        try:
            importlib.import_module(module_path)
        except ModuleNotFoundError as missing:
            if not (missing.name and module_path.startswith(missing.name)):
                raise
