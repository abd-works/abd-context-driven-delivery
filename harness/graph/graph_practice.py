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

    class_types: tuple[str, ...] = ()
    """Node types that are classes, which the source view opens a call into and folds in place."""

    member_types: tuple[str, ...] = ()
    """Node types that are a class's operations and properties, which the source view can open a call to."""

    class_node_type: str = ""
    """The node type this practice's checks run on as a whole class. Another practice's node that lies inside one of
    these classes skips this practice's checks, since they already ran on the class."""

    source_ordered_types: frozenset[str] = frozenset()
    """Node types the explorer lists in the order they appear in their files, not the order they were read."""

    extends: str = ""
    """The practice whose types this practice's schema builds on with ``is:``, such as a DDD entity that is a Clean
    Engineering class; its types also carry that practice's rules."""

    anchor_types: dict[str, str] = {}
    """The ``is:`` words another practice's schema uses to say one of its types is a type of this practice
    (``class`` for a Clean Engineering class), each with the node type it names."""

    rule_types: dict[str, tuple[str, ...]] = {}
    """Node types that also carry the rules the schema gives other types, such as every story node's rules on a story."""

    def align(self, node: Node) -> None:
        """Move node's source onto the lines that declare it, when a reader found it by a nearby line."""

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
        from harness.graph.schema_rules import PracticeSchema

        merged = self.checks(patterns)
        language = node.file_language
        if language and language not in _CODE_LANGUAGES:
            merged.update(self.language_rules(language))
        types = {node.type}
        anchor = PracticeSchema.load(self.name, patterns).anchor_type(node.type)
        if anchor:
            types.add(anchor)
        return {slug: rule for slug, rule in merged.items() if any(rule.applies_to(type_name) for type_name in types)}


class GraphOverlay:
    """What one pattern gives the graph on top of the practices: the nodes it reads and the rules it adds to each
    practice, which live in ``<pattern>/practices/<practice>/rules``."""

    direct_kinds: frozenset[str] = frozenset()
    """Relationship kinds of the pattern's schema that place a node as a child in the explorer tree; every other kind is
    listed under its kind's name."""

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    def display_of(self, kind: str) -> str:
        """How the explorer tree shows an edge of this pattern's kind: as a child, or under the kind's name."""
        return "direct" if kind in self.direct_kinds else "relationship"

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
