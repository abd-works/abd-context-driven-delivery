"""PracticeGraph — one registry for every practice node."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Type, TypeVar

from .graph_node import Kind, Node, Relationship
from .graph_rules import RuleRegistry, RuleViolation, closest_fidelity

T = TypeVar("T", bound=Node)

_CLASS_SEMANTICS = frozenset(
    {
        "OoadClass",
        "Entity",
        "EntityRoot",
        "ValueObject",
        "Repository",
        "DomainEvent",
        "DomainService",
    }
)


@dataclass
class RuleSlugs:
    names: List[str] = field(default_factory=list)

    @classmethod
    def read(cls, path: Path) -> "RuleSlugs":
        if not path.is_file():
            return cls()
        names = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        return cls(names)

    def write(self, path: Path) -> None:
        ordered = sorted(set(self.names))
        path.write_text(("\n".join(ordered) + "\n") if ordered else "", encoding="utf-8")


@dataclass
class Failures:
    parts: List[str] = field(default_factory=list)


@dataclass
class RuleTiming:
    slug: str
    seconds: float
    hits: int
    error: str = ""


class PracticeGraph:
    """Registry of nodes and relationships for one working area."""

    def __init__(self, root: Path, rule_registry: RuleRegistry | None = None) -> None:
        self.root = root.resolve()
        self.story_map = None
        self.ce_model = None
        self.nodes: Dict[str, Node] = {}
        self.relationships: List[Relationship] = []
        self._used_by: Dict[str, List[str]] = {}
        self._outgoing: Dict[str, List[Relationship]] = {}
        self._incoming: Dict[str, List[Relationship]] = {}
        self._classes_by_name: Dict[str, Node] = {}
        self._violations_by_node: Dict[str, List[RuleViolation]] = {}
        self.partial_failures: List[str] = []
        self.rule_timings: List[RuleTiming] = []
        self.rule_registry = rule_registry if rule_registry is not None else RuleRegistry.load()

    def working_context(self) -> Path:
        folder = self.root / ".context"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @classmethod
    def load(
        cls,
        path: str | Path,
        *,
        codeql_results: str | Path | None = None,
    ) -> "PracticeGraph":
        graph = cls(Path(path))
        from .codeql import CodeQL

        CodeQL(graph.root).populate(graph, results_path=codeql_results)
        graph.evaluate_rules()
        return graph

    def register(self, node: Node, node_id: Optional[str] = None) -> Node:
        node.join(self, node_id)
        self.nodes[node.node_id] = node
        if node._semantic_type_name in _CLASS_SEMANTICS:
            self._classes_by_name.setdefault(node.name, node)
        return node

    def _make_id(self, node: Node) -> str:
        practice = getattr(node, "practice", "node")
        semantic = getattr(node, "_semantic_type_name", type(node).__name__)
        return f"{practice}:{semantic}:{Node.slug(node.name)}:{id(node)}"

    def relate(self, edge: Relationship) -> Relationship:
        self.relationships.append(edge)
        self._outgoing.setdefault(edge.from_id, []).append(edge)
        self._incoming.setdefault(edge.to_id, []).append(edge)
        self._used_by.setdefault(edge.to_id, []).append(edge.from_id)
        return edge

    def nodes_of_type(self, cls: Type[T]) -> List[T]:
        return [n for n in self.nodes.values() if isinstance(n, cls)]

    def class_named(self, name: str) -> Optional[Node]:
        plain = (name or "").strip()
        if not plain:
            return None
        return self._classes_by_name.get(plain)

    def operation_named(self, class_name: str, operation_name: str) -> Optional[Node]:
        owner = self.class_named(class_name)
        if owner is None:
            return None
        for edge in self._outgoing.get(owner.node_id, ()):
            if edge.kind != Kind.OWNS:
                continue
            node = edge.to_node
            if node._semantic_type_name == "Operation" and node.name == operation_name:
                return node
        return None

    def evaluate_rules(
        self,
        slugs: RuleSlugs | None = None,
        skip: RuleSlugs | None = None,
        *,
        codeql_results: str | Path | None = None,
    ) -> Failures:
        wanted = set(slugs.names) if slugs is not None and slugs.names else None
        skipped = set(skip.names) if skip is not None and skip.names else None
        by_node = self.rule_registry.evaluate(self, slugs=wanted, skip=skipped)
        if wanted:
            self._merge_rule_hits(by_node, wanted)
        else:
            self._violations_by_node = by_node
        self._merge_codeql_violations(
            self._violations_by_node,
            Path(codeql_results) if codeql_results else None,
        )
        for node_id, violations in self._violations_by_node.items():
            node = self.nodes.get(node_id)
            if node is None:
                continue
            for violation in violations:
                try:
                    violation.direct = self._is_direct_violation(node, violation)
                except Exception as error:
                    self.record_partial_failure(
                        f"direct-flag {violation.rule_slug} on {getattr(node, 'name', node_id)}",
                        error,
                    )
        return Failures(list(self.partial_failures))

    def zero_hit_slugs(self) -> RuleSlugs:
        names: List[str] = []
        for item in self.rule_timings:
            if item.slug.startswith("run-queries:"):
                continue
            if item.error and item.error != "skipped":
                continue
            if item.hits == 0:
                names.append(item.slug)
        return RuleSlugs(names)

    def _merge_rule_hits(
        self,
        by_node: Dict[str, List[RuleViolation]],
        slugs: Optional[set],
    ) -> None:
        if slugs is None:
            for node_id, hits in by_node.items():
                self._violations_by_node.setdefault(node_id, []).extend(hits)
            return
        for node_id, existing in list(self._violations_by_node.items()):
            self._violations_by_node[node_id] = [
                hit for hit in existing if hit.rule_slug not in slugs
            ]
        for node_id, hits in by_node.items():
            self._violations_by_node.setdefault(node_id, []).extend(hits)

    def record_partial_failure(self, part: str, error: BaseException) -> None:
        import logging
        import traceback

        message = f"{part}: {type(error).__name__}: {error}"
        logging.getLogger("harness.knowledge_graph").error(message, exc_info=True)
        self.partial_failures.append(message)
        log_dir = self.root / ".codeql" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "partial-failures.log").open("a", encoding="utf-8") as log:
            log.write(message + "\n")
            log.write("".join(traceback.format_exception(error)))
            log.write("\n")

    def record_rule_timing(
        self,
        slug: str,
        seconds: float,
        hits: int,
        error: str = "",
    ) -> None:
        self.rule_timings.append(RuleTiming(slug, seconds, hits, error))
        log_dir = self.root / ".codeql" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        suffix = f"  {error}" if error else ""
        line = f"{seconds:7.2f}s  hits={hits:4d}  {slug}{suffix}"
        with (log_dir / "query-run.log").open("a", encoding="utf-8") as log:
            log.write(line + "\n")
            log.flush()
        print(line, flush=True)

    def _is_direct_violation(self, node: Node, violation: RuleViolation) -> bool:
        closest = closest_fidelity(node.practice, node._semantic_type_name)
        if violation.fidelity is not None:
            return violation.fidelity == closest
        return violation.practice == node.practice

    def _merge_codeql_violations(
        self,
        by_node: Dict[str, List[RuleViolation]],
        codeql_results: Path | None,
    ) -> None:
        import json

        from .codeql import CodeQL

        export_path = CodeQL(self.root).results_path(codeql_results)
        if export_path is None:
            return
        raw = json.loads(export_path.read_text(encoding="utf-8"))
        for entry in raw.get("rule_violations", []):
            node = self._resolve_violation_node(entry)
            if node is None:
                continue
            by_node.setdefault(node.node_id, []).append(
                RuleViolation(
                    rule_slug=entry.get("rule_slug", ""),
                    message=entry.get("message", ""),
                    practice=entry.get("practice", ""),
                    fidelity=entry.get("fidelity") or None,
                    node_id=node.node_id,
                    location=entry.get("file", ""),
                    line=int(entry.get("line") or 0),
                    source="codeql",
                )
            )

    def _resolve_violation_node(self, entry: dict):
        node_id = entry.get("node_id") or ""
        if node_id and node_id in self.nodes:
            return self.nodes[node_id]
        semantic = entry.get("semantic_type") or ""
        name = entry.get("node_name") or ""
        for node in self.nodes.values():
            if node._semantic_type_name != semantic:
                continue
            if node.name != name:
                continue
            return node
        return None

    @property
    def dot_graph(self) -> str:
        from .dot_graph import dot_graph_from_roots

        owned = {edge.to_id for edge in self.relationships if edge.kind == Kind.OWNS}
        roots = [node for node in self.nodes.values() if node.node_id not in owned]
        if not roots:
            return "digraph practice_graph {}\n"
        return dot_graph_from_roots(roots, graph_name="practice_graph")
