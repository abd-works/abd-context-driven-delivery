"""FilterRequest, FilterChoices and Filter. What a call asks the graph's explorer to keep, the choices the explorer
offers for a filter, and the filter made for one request, which matches the nodes it keeps."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, TypedDict

from harness.graph.explorer import FilteredNode
from harness.graph.node_metric import METRIC_TYPE, METRICS_GROUP
from harness.installation.data_class import data_field

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node, Source
    from harness.graph.graph_rules_collection import GraphRule


class FilterRequest(TypedDict, total=False):
    """What a call to ``graph.return_nodes``, ``graph.explorer_trees``, or ``graph.explorer_branch`` asks the filter
    for: practice(s), type(s), a name, rules, relationships, whether only violations, and path(s). A key that takes a
    list also takes one value under its singular name."""

    practices: list[str]
    practice: str
    types: list[str]
    type: str
    name: str
    rules: list[str]
    relationships: list[str]
    violations: bool
    paths: list[str]
    path: str


class FilterChoices:
    """The choices the explorer's filter offers once practices and node types are chosen: the node types the chosen
    practices hold, those chosen, and the relationships and rules of the chosen ones, or of every offered one when none
    is chosen. Made for one question and kept by no one, so no choice stays on the graph between calls."""

    def __init__(self, graph: Graph, practices: list[str], node_types: list[str], practices_before: list[str] | None = None) -> None:
        self._graph = graph
        self._practices = list(practices)
        self._node_types = self._chosen(list(node_types), practices_before)

    def _chosen(self, node_types: list[str], before: list[str] | None) -> list[str]:
        """The node types chosen. After a change of practice, when before names the practices chosen before and
        node_types those chosen then: the ones the new practices still hold stay chosen, and every node type of each
        practice added is chosen. A change from or to every practice chooses every node type the new choice holds."""
        if before is None:
            return node_types
        if not before or not self._practices:
            return self.offered_node_types
        kept = set(node_types)
        added = {node_type for key in self._practices if key not in before for node_type in self._node_types_of(key)}
        return [node_type for node_type in self.offered_node_types if node_type in kept | added]

    @property
    @data_field
    def node_types(self) -> list[str]:
        """The node types chosen."""
        return list(self._node_types)

    @property
    @data_field
    def offered_node_types(self) -> list[str]:
        """Every node type the chosen practices hold, or every loaded practice's when none is chosen."""
        found: list[str] = []
        for key in self._scope():
            for node_type in self._node_types_of(key):
                if node_type not in found:
                    found.append(node_type)
        return found

    @property
    @data_field
    def relationships(self) -> list[str]:
        """The edge kinds the chosen node types sit on, of every offered node type when none is chosen, and last the
        metrics group when a node of those types holds a metric."""
        types = set(self._node_types or self.offered_node_types)
        found: list[str] = []
        for part in self._parts():
            for edge_type in sorted(part.edge_index.types.values(), key=lambda edge_type: edge_type.order):
                if edge_type.kind in found or not edge_type.is_offered:
                    continue
                if any(edge.parent.type in types or edge.child.type in types for edge in part.edge_index.of(edge_type.kind)):
                    found.append(edge_type.kind)
        return [*found, METRICS_GROUP] if self._holds_a_metric(types) else found

    def _holds_a_metric(self, types: set[str]) -> bool:
        """Whether a node of types, in a chosen practice, holds a metric: only the node types a practice says can hold
        one are looked at, so a practice with no limit rule costs nothing."""
        opened = self._graph.practices.opened
        readings = [opened[key].reading for key in self._scope() if key in opened]
        return any(
            reading.metrics_of(node)
            for reading in readings
            for node_type in reading.metric_node_types
            if node_type in types
            for node in reading.in_graph.nodes(node_type)
        )

    @property
    @data_field
    def rules(self) -> list[str]:
        """The rules the chosen node types run or fail, of every offered node type when none is chosen."""
        types = set(self._node_types or self.offered_node_types)
        found: set[str] = set()
        for part in self._parts():
            found.update(part.rule_run.rule_labels_for(types))
        return sorted(found)

    def _scope(self) -> list[str]:
        return list(self._practices) if self._practices else list(self._graph.practices.opened)

    def _parts(self) -> list:
        opened = self._graph.practices.opened
        return [opened[key].reading.in_graph for key in self._scope() if key in opened]

    def _node_types_of(self, key: str) -> list[str]:
        practice = self._graph.practices.opened.get(key)
        return list(practice.reading.in_graph.node_types) if practice is not None else []


class Filter:
    """The filter one request asks for, made for that request: the practices, node types, name, rules, relationships,
    violations, and paths it names. It matches a node, lists a file, and collects the nodes it keeps under roots."""

    def __init__(self, graph: Graph, request: FilterRequest | None = None) -> None:
        request = request or {}
        self.graph = graph
        self.practices = self._listed(request, "practices", "practice")
        self.node_types = self._listed(request, "types", "type")
        self.name = request.get("name") or ""
        self.paths = self._listed(request, "paths", "path")
        self.violations = bool(request.get("violations"))
        self.rules = list(request.get("rules") or [])
        self.relationships = list(request.get("relationships") or [])

    def _listed(self, request: FilterRequest, many: str, one: str) -> list[str]:
        """A request key that takes a list or a single value, such as ``types`` or ``type``."""
        return list(request.get(many) or ([request[one]] if request.get(one) else []))

    def matches(self, node: Node) -> bool:
        """True when the node is of a chosen practice and type, has the chosen name, fails a chosen rule when only
        violations are wanted, sits on a chosen relationship, and lies under a chosen path."""
        if node.type == "Practice" or node.type == node.name:
            return False
        if node.type == METRIC_TYPE:
            # A metric is shown wherever the node it measures is: it sits under that node's metrics group.
            return self.matches(node.parent.parent)
        if self.name and node.name != self.name:
            return False
        if self.node_types and node.type not in self.node_types:
            return False
        if self.practices and node.practice.key not in self.practices:
            return False
        if self.violations and not self._fails_selected_rule(node):
            return False
        if self.relationships and not self._on_relationship(node):
            return False
        return not self.paths or self._listed_or_below_listed(node)

    def lists(self, file: str) -> bool:
        """True when file, named as a viewer lists it, is one of the chosen paths or sits under one: the same test a
        node's file passes to stay in the trees, for a file a link names, which no node stands for."""
        return self._under_paths(file)

    def collect(self, roots: Iterable[Node]) -> list[FilteredNode]:
        """Every node under roots, the roots included, that this filter matches, each once, with its ancestors' names
        and the rules this filter shows."""
        walk = _FilterWalk(self)
        for root in roots:
            walk.visit(root, [])
        return walk.found

    def _listed_or_below_listed(self, node: Node) -> bool:
        """True when node's file is listed, or a node above it was read from a listed file: a story listed by its story
        map holds the scenarios and steps read for it from scenarios files the list leaves out. A node written in several
        formats (``Node.places``) is listed by any of its files."""
        above: Node | None = node
        while above is not None:
            if self._source_listed(above.source) or any(self._under_paths(place.file) for place in above.places.values()):
                return True
            above = above.parent
        return False

    def _source_listed(self, source: Source) -> bool:
        return self._under_paths(source.file) or self._under_paths(self._named_from_folder(source))

    def _named_from_folder(self, source: Source) -> str | None:
        """source's file named from the graph's folder, as a viewer listing the folder names it: a practice that reads from
        a folder of its own, such as Stories from the project's .context, names its files from there; a file above the
        folder is named with `..`, as Session names the paths it filters by."""
        folder = self.graph.folder
        if not folder or not source.root or not source.file:
            return None
        return os.path.relpath(os.path.normpath(Path(source.root, source.file)), folder).replace("\\", "/")

    def _under_paths(self, file: str | None) -> bool:
        """True when ``file`` is one of the chosen paths or sits under one."""
        location = self._posix(file)
        folders = [self._posix(prefix) for prefix in self.paths]
        return any(folder and (location == folder or location.startswith(folder + "/")) for folder in folders)

    def _posix(self, path: str | None) -> str:
        """path with forward slashes and no slash at either end, as a node names its file."""
        return str(path or "").replace("\\", "/").strip("/")

    def _fails_selected_rule(self, node: Node) -> bool:
        hits = node.failed_rules
        if not hits:
            return False
        if not self.rules:
            return True
        return any(self._label_hits(node, label, hits) for label in self.rules)

    def failing_rules(self, node: Node) -> list[GraphRule]:
        """The rules node fails that this filter chooses, by slug or by ``practice.node.rule`` label; every one it fails
        when it chooses none."""
        return [rule for rule in node.rules.graph_rules if rule.is_failing and (not self.rules or any(self._label_hits(node, label, [rule.slug]) for label in self.rules))]

    def _label_hits(self, node: Node, label: str, hits: list[str]) -> bool:
        parts = label.split(".")
        if len(parts) < 3:
            return label in hits
        slug, node_type, practice = parts[-1], parts[-2], parts[-3]
        if slug not in hits or node.type != node_type:
            return False
        return node.practice.key == practice

    def _on_relationship(self, node: Node) -> bool:
        if METRICS_GROUP in self.relationships and node.practice.reading.metrics_of(node):
            return True
        for kind in self.relationships:
            for edge in node.practice.reading.in_graph.edge_index.of(kind):
                if edge.parent is node or edge.child is node:
                    return True
        return False


class _FilterWalk:
    """One walk of a filter down the trees it collects from: the nodes it matched so far, and every node it has seen,
    so a node reached twice is collected once."""

    def __init__(self, wanted: Filter) -> None:
        self._wanted = wanted
        self.found: list[FilteredNode] = []
        self._seen: set[int] = set()

    def visit(self, node: Node, ancestors: list[str]) -> None:
        """Collect node, when the filter matches it, and then each node under it."""
        if id(node) in self._seen:
            return
        self._seen.add(id(node))
        wanted = self._wanted
        if wanted.matches(node):
            self.found.append(FilteredNode(node, ancestors, node.rules.chosen(wanted.violations, list(wanted.rules))))
        chain = [*ancestors, node.name]
        for child in node.children:
            self.visit(child, chain)
