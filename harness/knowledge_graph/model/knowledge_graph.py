"""KnowledgeGraph — aggregate of practice graphs; always the working copy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import mcp
from installation.files import Skill

from .graph_filter import expand_ids, match_node, parse_filter
from .graph_node import Kind
from .practice_graph import PracticeGraph


@agent_toolset
class KnowledgeGraph:
    """Always reads the working copy — never master."""

    domain_slug = "knowledge-graph"

    def __init__(
        self,
        practice_graphs: List[PracticeGraph] | None = None,
        root: Path | None = None,
    ) -> None:
        self._practice_graphs = list(practice_graphs or [])
        self._root = Path(root) if root is not None else None

    @property
    def root(self) -> Path:
        if self._root is not None:
            return self._root
        if self._practice_graphs:
            return self._practice_graphs[0].root
        return Path.cwd()

    @property
    def practice_graphs(self) -> List[PracticeGraph]:
        return list(self._practice_graphs)

    def refresh_master(self) -> KnowledgeGraph:
        from .codeql import CodeQL
        from .practice_graph import PracticeGraph

        codeql = CodeQL(self.root)
        master = codeql.rewrite_master()
        graph = PracticeGraph(self.root)
        codeql.populate(graph, database=master, results_path=master / "practice-graph.json")
        codeql.copy_master_to_working_copy()
        self._practice_graphs = [graph]
        return self

    def update_working_copy(self, paths: list[Path]) -> KnowledgeGraph:
        from .codeql import CodeQL
        from .practice_graph import PracticeGraph

        codeql = CodeQL(self.root)
        working = codeql.extract_working_copy(list(paths))
        graph = PracticeGraph(self.root)
        codeql.populate(
            graph,
            database=working,
            results_path=working / "practice-graph.json",
        )
        from .loader import attach_story_tests

        attach_story_tests(graph, list(paths))
        self._practice_graphs = [graph]
        return self

    def validate(self, rule=None) -> KnowledgeGraph:
        from .codeql import CodeQL
        from .practice_graph import RuleSlugs

        slugs = RuleSlugs([rule.slug]) if rule is not None else None
        working = CodeQL(self.root).working_copy
        instructions: list[str] = []
        for graph in self._practice_graphs:
            graph.evaluate_rules(slugs=slugs, database=working)
            instructions.extend(self._markdown_instructions(graph, rule))
        self.markdown_instructions = "\n".join(instructions)
        return self

    def _markdown_instructions(self, graph, rule) -> list[str]:
        texts: list[str] = []
        for item in graph.rule_registry.rules:
            if rule is not None and item.slug != rule.slug:
                continue
            if getattr(item, "graphQuery", None) is not None:
                continue
            texts.append(item.validate())
        return texts

    @mcp
    @Skill
    @agent_tool
    def return_nodes(
        self,
        filter: str | dict | None = None,
        root: str | None = None,
    ) -> str:
        """Return matching graph nodes as JSON. Filter with a dotted path (Class.operation) or a dict of name, node_id, file, rule, rules, practice, practices, semantic_type, semantic_types, violations, related_to. Always includes ancestors, children, and relationships of matched nodes. Optional root is a folder that already has .codeql/results/practice-graph.json."""
        if root:
            self._root = Path(root)
            self._practice_graphs = []
        return json.dumps(self._nodes_as_json(filter), indent=2)

    def _graphs(self) -> List[PracticeGraph]:
        if self._practice_graphs:
            return self._practice_graphs
        try:
            from .codeql import CodeQL

            graph = PracticeGraph(self.root)
            CodeQL(self.root).populate(graph, populate=False)
            self._practice_graphs = [graph]
        except Exception:
            self._practice_graphs = []
        return self._practice_graphs

    def _nodes_as_json(self, filter) -> list[dict]:
        parsed = parse_filter(filter)
        matched: list[dict] = []
        for graph in self._graphs():
            seeds = {
                node.node_id
                for node in graph.nodes.values()
                if match_node(node, graph, parsed)
            }
            kept = expand_ids(seeds, graph) if parsed else set(graph.nodes)
            for node in graph.nodes.values():
                if node.node_id not in kept:
                    continue
                matched.append(
                    self._node_as_json(
                        node,
                        graph,
                        seed=node.node_id in seeds,
                        kept=kept,
                    )
                )
        return matched

    def _nodes_along(self, graph, parts: list[str]):
        keys = [part.strip().casefold() for part in parts if part.strip()]
        if not keys:
            return list(graph.nodes.values())
        current = [node for node in graph.nodes.values() if self._key_matches(node, keys[0])]
        for key in keys[1:]:
            current = [
                child
                for node in current
                for child in self._children(node)
                if self._key_matches(child, key)
            ]
        return current

    def _key_matches(self, node, key: str) -> bool:
        return self._name_key(node) == key or node.node_id.casefold() == key

    def _name_key(self, node) -> str:
        return str(getattr(node, "name", "") or node.semantic_type()).casefold()

    def _children(self, node):
        owned = node.related(Kind.OWNS)
        return owned if owned else node.related()

    def _dotted_path(self, node) -> str:
        names = [str(getattr(node, "name", "") or node.semantic_type())]
        current = node
        for _ in range(8):
            parents = current.related(Kind.BELONGS_TO) or current.related(
                Kind.OWNS, direction="in"
            )
            if not parents:
                break
            current = parents[0]
            names.append(str(getattr(current, "name", "") or current.semantic_type()))
        return ".".join(reversed(names))

    def _node_as_json(self, node, graph, seed: bool = True, kept: set | None = None) -> dict:
        src = getattr(node, "source", None)
        hits = graph._violations_by_node.get(node.node_id, [])
        kept_ids = kept if kept is not None else {node.node_id}
        relationships = []
        for edge in list(graph._outgoing.get(node.node_id, ())) + list(
            graph._incoming.get(node.node_id, ())
        ):
            if edge.from_id not in kept_ids or edge.to_id not in kept_ids:
                continue
            other = edge.to_node if edge.from_id == node.node_id else edge.from_node
            relationships.append(
                {
                    "kind": edge.kind,
                    "from_id": edge.from_id,
                    "to_id": edge.to_id,
                    "name": getattr(other, "name", None) or other.semantic_type(),
                }
            )
        return {
            "path": self._dotted_path(node),
            "node_id": node.node_id,
            "name": getattr(node, "name", None) or node.semantic_type(),
            "practice": getattr(node, "practice", "") or "",
            "semantic_type": node.semantic_type(),
            "seed": seed,
            "source": None
            if src is None
            else {
                "file": str(getattr(src, "file", "") or ""),
                "start_line": int(getattr(src, "line", 0) or 0),
                "end_line": int(getattr(src, "end_line", 0) or 0),
                "text": str(getattr(src, "text", "") or ""),
            },
            "relationships": relationships,
            "violations": [
                {
                    "rule_slug": hit.rule_slug,
                    "message": hit.message,
                    "practice": hit.practice,
                    "fidelity": hit.fidelity,
                }
                for hit in hits
            ],
        }
