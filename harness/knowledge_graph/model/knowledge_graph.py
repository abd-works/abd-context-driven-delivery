"""KnowledgeGraph — aggregate of practice graphs; always the working copy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.mcp.mcp_server import mcp
from installation.files import Skill

from .graph_filter import Filter
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

    @mcp
    @Skill
    @agent_tool
    def reload_working_copy(self, root: str | None = None) -> KnowledgeGraph:
        """Reload the working copy from the tree, populate from it, and copy it to master. Optional root is the repo folder that already has a CodeQL database."""
        from .codeql import CodeQL
        from .practice_graph import PracticeGraph

        if root:
            self._root = Path(root)
            self._practice_graphs = []
        codeql = CodeQL(self.root)
        working = codeql.rewrite_working_copy()
        graph = PracticeGraph(self.root)
        codeql.populate(
            graph,
            database=working,
            results_path=working / "practice-graph.json",
        )
        codeql.copy_working_copy_to_master()
        self._practice_graphs = [graph]
        return self

    @mcp
    @Skill
    @agent_tool
    def create_database(self, root: str | None = None) -> KnowledgeGraph:
        """Create a CodeQL master database in the repo folder and copy it to the working copy. Optional root is the repo folder to point the Knowledge Graph at."""
        from .codeql import CodeQL

        if root:
            self._root = Path(root)
            self._practice_graphs = []
        codeql = CodeQL(self.root)
        codeql.rewrite_master()
        codeql.copy_master_to_working_copy()
        self._practice_graphs = []
        return self

    @mcp
    @Skill
    @agent_tool
    def update_working_copy(
        self,
        paths: list[str] | None = None,
        root: str | None = None,
    ) -> KnowledgeGraph:
        """Update the working copy from dirty files, populate from it, and attach story tests. Pass paths as repo-relative or absolute file paths. Optional root is the repo folder that already has a CodeQL database."""
        from .codeql import CodeQL
        from .practice_graph import PracticeGraph

        if root:
            self._root = Path(root)
            self._practice_graphs = []
        dirty = [Path(path) for path in (paths or [])]
        codeql = CodeQL(self.root)
        working = codeql.extract_working_copy(dirty)
        graph = PracticeGraph(self.root)
        codeql.populate(
            graph,
            database=working,
            results_path=working / "practice-graph.json",
        )
        from .loader import attach_story_tests

        attach_story_tests(graph, dirty)
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
        filter: Filter | None = None,
        root: str | None = None,
    ) -> str:
        """Return matching graph nodes as JSON. Always includes ancestors, children, and relationships of matched nodes. Optional root is a folder that already has .codeql/results/practice-graph.json."""
        if root:
            self._root = Path(root)
            self._practice_graphs = []
        return json.dumps(self._nodes_as_json(Filter.from_value(filter)), indent=2)

    @mcp
    @Skill
    @agent_instructions
    def fix_violations(
        self,
        filter: Filter | None = None,
        root: str | None = None,
    ) -> str:
        """Fix Knowledge Graph rule violations under a node and its children. Always includes the node and its children. Only nodes that have violations are included. Optional root is a folder that already has .codeql/results/practice-graph.json."""
        return self._violation_prompt_text(Filter.from_value(filter), root)

    def _graphs(self) -> List[PracticeGraph]:
        if self._practice_graphs:
            return self._practice_graphs
        try:
            from .codeql import CodeQL

            graph = PracticeGraph(self.root)
            codeql = CodeQL(self.root)
            codeql.populate(graph, populate=False)
            graph.evaluate_rules(database=codeql.working_copy)
            self._practice_graphs = [graph]
        except Exception:
            self._practice_graphs = []
        return self._practice_graphs

    def _nodes_as_json(self, filt: Filter) -> list[dict]:
        matched: list[dict] = []
        for graph in self._graphs():
            seeds = {
                node.node_id
                for node in graph.nodes.values()
                if filt.matches(node)
            }
            kept = filt.expand_ids(seeds, graph) if filt.constrains else set(graph.nodes)
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
        hits = graph.violations_for(node)
        kept_ids = kept if kept is not None else {node.node_id}
        relationships = []
        for edge in graph.edges_at(node):
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

    def _violation_prompt_text(self, filt: Filter, root: str | None = None) -> str:
        if root:
            self._root = Path(root)
            self._practice_graphs = []
        prompts = [
            prompt
            for graph in self._graphs()
            for prompt in self._graph_violation_prompts(graph, filt)
        ]
        return "\n\n---\n\n".join(prompts)

    def _graph_violation_prompts(self, graph, filt: Filter) -> list[str]:
        kept = self._violation_subtree_ids(graph, filt)
        hit = filt.without_scope()
        hit.violations = True
        prompts: list[str] = []
        for node in graph.nodes.values():
            if node.node_id not in kept:
                continue
            if not hit.matches(node):
                continue
            self._prompt_filter = hit
            prompts.extend(self._node_violation_prompts(node))
        return prompts

    def _violation_subtree_ids(self, graph, filt: Filter) -> set:
        scope = filt.scope()
        if not scope.constrains:
            return set(graph.nodes)
        seeds = {
            node.node_id
            for node in graph.nodes.values()
            if filt.matches(node)
        }
        return filt.subtree_ids(seeds, graph)

    def _node_violation_prompts(self, node) -> list[str]:
        filt = self._prompt_filter
        graph = node.graph
        rules = filt.listed(("rules", "rule"))
        prompts: list[str] = []
        for hit in graph.violations_for(node):
            if rules and hit.rule_slug not in rules:
                continue
            prompts.append(self._violation_prompt(node, hit, graph))
        return prompts

    def _violation_prompt(self, node, hit, graph) -> str:
        file = self._source_span(getattr(node, "source", None))
        body = self._rule_body(graph, hit.rule_slug)
        return "\n".join(
            line
            for line in (
                "Fix this Knowledge Graph rule violation.",
                f"Node: {self._dotted_path(node)} ({node.semantic_type()})",
                f"File: {file}" if file else "",
                f"Rule: {hit.rule_slug}",
                f"Practice: {hit.practice}" if getattr(hit, "practice", "") else "",
                f"Fidelity: {hit.fidelity}" if getattr(hit, "fidelity", "") else "",
                body,
                f"Violation: {hit.message}",
            )
            if line
        )

    def _source_span(self, src) -> str:
        if src is None:
            return ""
        file = str(getattr(src, "file", "") or "")
        if not file:
            return ""
        start = int(getattr(src, "line", 0) or 0)
        end = int(getattr(src, "end_line", 0) or 0)
        if start >= 1:
            return f"{file}:{start}-{end}"
        return file

    def _rule_body(self, graph, slug: str) -> str:
        for item in getattr(graph.rule_registry, "rules", []) or []:
            if getattr(item, "slug", "") == slug:
                return str(
                    getattr(item, "body", None) or getattr(item, "markdown", None) or ""
                )
        return ""
