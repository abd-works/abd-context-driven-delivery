"""KnowledgeGraph — aggregate of practice graphs; always the working copy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from installation.destination import Destination
from installation.files import Skill


class Mcp(Destination):
    flag = "_mcp"

    def __new__(cls, fn=None):
        inst = object.__new__(cls)
        inst.name = None
        if callable(fn):
            return inst.annotate(fn)
        return inst

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

    @Mcp
    @Skill
    @agent_tool
    def return_nodes(self, filter: str | dict | None = None) -> str:
        """Return matching graph nodes as JSON. Filter with a dotted path (Class.operation) or a dict of name, node_id, file, rule, practice, semantic_type, violations."""
        return json.dumps(self._nodes_as_json(filter), indent=2)

    def _graphs(self) -> List[PracticeGraph]:
        if self._practice_graphs:
            return self._practice_graphs
        try:
            self._practice_graphs = [PracticeGraph.load(self.root)]
        except Exception:
            self._practice_graphs = []
        return self._practice_graphs

    def _parse_filter(self, filter) -> dict:
        if filter in (None, "", {}, []):
            return {}
        if isinstance(filter, str):
            stripped = filter.strip()
            if stripped.startswith("{"):
                return json.loads(stripped)
            return {"path": stripped}
        return dict(filter)

    def _nodes_as_json(self, filter) -> list[dict]:
        parsed = self._parse_filter(filter)
        matched: list[dict] = []
        for graph in self._graphs():
            for node in graph.nodes.values():
                if self._node_matches(node, graph, parsed):
                    matched.append(self._node_as_json(node, graph))
        return matched

    def _node_matches(self, node, graph, parsed: dict) -> bool:
        path = str(parsed.get("path") or "").strip()
        if path:
            hits = {item.node_id for item in self._nodes_along(graph, path.split("."))}
            if node.node_id not in hits:
                return False
        return self._field_matches(node, graph, parsed)

    def _field_matches(self, node, graph, parsed: dict) -> bool:
        name = parsed.get("name")
        if name and self._name_key(node) != str(name).casefold():
            return False
        node_id = parsed.get("node_id")
        if node_id and node.node_id != str(node_id):
            return False
        practice = parsed.get("practice")
        if practice and (getattr(node, "practice", "") or "") != practice:
            return False
        semantic = parsed.get("semantic_type")
        if semantic and node.semantic_type() != semantic:
            return False
        return self._source_and_rule_match(node, graph, parsed)

    def _source_and_rule_match(self, node, graph, parsed: dict) -> bool:
        file = str(parsed.get("file") or "").replace("\\", "/").casefold()
        src = str(getattr(getattr(node, "source", None), "file", "") or "").replace("\\", "/")
        if file and file not in src.casefold():
            return False
        rule = str(parsed.get("rule") or "")
        hits = graph._violations_by_node.get(node.node_id, [])
        if rule and not any(hit.rule_slug == rule for hit in hits):
            return False
        if parsed.get("violations") in (True, "true", "True", 1) and not hits:
            return False
        return True

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

    def _node_as_json(self, node, graph) -> dict:
        src = getattr(node, "source", None)
        hits = graph._violations_by_node.get(node.node_id, [])
        return {
            "path": self._dotted_path(node),
            "node_id": node.node_id,
            "name": getattr(node, "name", None) or node.semantic_type(),
            "practice": getattr(node, "practice", "") or "",
            "semantic_type": node.semantic_type(),
            "source": None
            if src is None
            else {
                "file": str(getattr(src, "file", "") or ""),
                "start_line": int(getattr(src, "line", 0) or 0),
                "end_line": int(getattr(src, "end_line", 0) or 0),
                "text": str(getattr(src, "text", "") or ""),
            },
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
