"""How one practice takes part in the knowledge graph: the part of a practice the graph that holds it talks to."""
from __future__ import annotations

import functools
import importlib
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from harness.guidance.guidance import PracticeGuidance


class HoldingGraph(Protocol):
    """The knowledge graph that holds a practice, as a practice's reading names it: harness/graph's *Graph* answers it.
    harness/graph sits above this module, so only what every reading asks of the graph is named here, as the action
    catalogue names the fidelity an action runs on; a practice's own kind of reading imports harness/graph and reaches
    the rest of the graph there."""

    @property
    def practices(self) -> Iterable[object]: ...


class HeldRuleRun(Protocol):
    """The run of a practice's graph rules in its graph, as a reading asks it for the rules it checks."""

    @property
    def checks(self) -> Mapping[str, object]: ...


class HeldNodes(Protocol):
    """The practice's part of the graph that holds it (harness/graph's *PracticeNodes*): its nodes and edges, the node
    types it offers, and the run of its rules."""

    @property
    def rule_run(self) -> HeldRuleRun: ...

    def offer_node_types(self, types: Iterable[str]) -> None: ...


def rules_in(module_path: str) -> dict[str, Any]:
    """The graph rules a rules module lists, by slug: its ``BY_SLUG``, else each of its ``RULES``. A module that is not
    there has none."""
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


class PracticeReading:
    """How one practice takes part in the knowledge graph: which of its node types the graph treats as classes,
    members, or source-ordered, how it reads its nodes from the working copy, and the graph rules it checks. The graph
    names no practice, so these words live with the practice: each practice holds one, made from the kind of reading
    its class names (``PracticeGuidance.reading_type``), and the graph that holds the practice talks to it.

    The graph hands it the graph and the practice's place there (``held_in``): code holding the practice asks
    ``practice.reading.in_graph`` for its nodes. A practice that reads files from the working copy reads them in its own
    kind of reading (``read_working_copy``), after the practices it names in ``reads_after``, and links its nodes to
    theirs there."""

    reads_after: tuple[str, ...] = ()
    """The practices whose nodes this one reads while it reads its own, by key; the graph reads them first, so this one
    links its nodes to theirs once its own are read."""

    node_types: tuple[str, ...] = ()
    """Node types the graph explorer offers for this practice even before any node of them is read."""

    class_types: tuple[str, ...] = ()
    """Node types that are classes, which the source view opens a call into and folds in place."""

    member_types: tuple[str, ...] = ()
    """Node types that are a class's operations and properties, which the source view can open a call to."""

    class_node_type: str = ""
    """The node type this practice's checks run on as a whole class. Another practice's node that lies inside one of
    these classes skips this practice's checks, since they already ran on the class."""

    source_ordered_types: frozenset[str] = frozenset()
    """Node types the explorer lists in the order they appear in their files, not the order they were read."""

    anchor_types: dict[str, str] = {}
    """The ``is:`` words another practice's schema uses to say one of its types is a type of this practice
    (``class`` for a Clean Engineering class), each with the node type it names."""

    rule_types: dict[str, tuple[str, ...]] = {}
    """Node types that also carry the rules the schema gives other types, such as every story node's rules on a story."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self.practice = practice
        # The graph that holds the practice (harness/graph's *Graph*) and the practice's part of it (its
        # *PracticeNodes*: its root node, its nodes, and its edges); none until a graph holds the practice.
        self.graph: HoldingGraph | None = None
        self.in_graph: HeldNodes | None = None

    def held_in(self, graph: HoldingGraph, nodes: HeldNodes) -> None:
        """Be read in graph, where nodes, the practice's part of it, holds the practice's nodes and edges."""
        self.graph = graph
        self.in_graph = nodes

    def read(self) -> None:
        """Read the practice into its graph from the working copy that graph is loading: offer its node types, then read
        its nodes."""
        self.in_graph.offer_node_types(self.node_types)
        self.read_working_copy()

    def read_working_copy(self) -> None:
        """Read this practice's nodes and edges into its graph, and link them to the nodes of the practices it reads
        after. A practice that reads no files from the working copy reads nothing."""

    def reads_model_document(self, file: Path) -> bool:
        """Whether this practice reads file, a model document in a ``.context`` folder, in a model format of its own,
        such as DDD's domain model; another practice whose documents share its name pattern then leaves it alone, as
        its own format would misread it. A practice that reads no model document of its own reads none."""
        return False

    @functools.cached_property
    def graph_checks(self) -> dict[str, Any]:
        """Every graph rule (a *PracticeGraphRule*) this practice checks, by slug; read once."""
        return self.own_graph_checks()

    @property
    def package(self) -> str:
        """The Python package that holds the practice, such as ``cdd_guidance.practices.stories``."""
        return type(self.practice).__module__.rsplit(".", 1)[0]

    def own_graph_checks(self) -> dict[str, Any]:
        """The graph rules the practice's ``rules`` package lists; a practice that checks more overrides this."""
        return rules_in(f"{self.package}.rules")

    def checks(self) -> dict[str, Any]:
        """The graph rules this practice checks, with those the pattern overlays its graph applies add to it, by slug;
        its own alone for a practice no graph holds."""
        return self.in_graph.rule_run.checks if self.in_graph is not None else dict(self.graph_checks)
