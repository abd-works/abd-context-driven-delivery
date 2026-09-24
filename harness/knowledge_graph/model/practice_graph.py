"""PracticeGraph — one registry for every practice node."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar

from .graph_node import Kind, Node, Relationship
from .graph_rules import (
    RuleRegistry,
    RuleViolation,
    closest_fidelity,
    drop_cloned_operation_hits,
)

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
    def from_path(cls, path: Path) -> "RuleSlugs":
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
        self._violations_by_node: Dict[str, List[RuleViolation]] = {}
        self.partial_failures: List[str] = []
        self.rule_timings: List[RuleTiming] = []
        self.rule_registry = rule_registry if rule_registry is not None else RuleRegistry.load()
        self.modules: Dict[str, Node] = {}
        self.epics: Dict[str, Node] = {}
        self.descriptions: Dict[str, Node] = {}

    def violations_for(self, node: Node) -> List[RuleViolation]:
        return list(self._violations_by_node.get(node.node_id, []))

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
        populate: bool = True,
    ) -> "PracticeGraph":
        from .loader import GraphLoader

        return GraphLoader(path, codeql_results).load(evaluate=populate)

    def register(self, node: Node, node_id: Optional[str] = None) -> Node:
        node.join(self, node_id)
        self.nodes[node.node_id] = node
        return node

    def id_for(self, node: Node) -> str:
        practice = getattr(node, "practice", "node")
        semantic = node.semantic_type()
        return f"{practice}:{semantic}:{Node().slug(node.name)}:{id(node)}"

    def relate(self, edge: Relationship) -> Relationship:
        self.relationships.append(edge)
        self._used_by.setdefault(edge.to_id, []).append(edge.from_id)
        self._outgoing.setdefault(edge.from_id, []).append(edge)
        self._incoming.setdefault(edge.to_id, []).append(edge)
        return edge

    def edges_from(self, node: Node) -> List[Relationship]:
        return list(self._outgoing.get(node.node_id, ()))

    def edges_to(self, node: Node) -> List[Relationship]:
        return list(self._incoming.get(node.node_id, ()))

    def edges_at(self, node: Node) -> List[Relationship]:
        return self.edges_from(node) + self.edges_to(node)

    def users_of(self, node: Node) -> List[str]:
        return list(self._used_by.get(node.node_id, []))

    def named_nodes(self) -> Dict[str, list]:
        names: Dict[str, list] = {}
        for candidate in self.nodes.values():
            names.setdefault(getattr(candidate, "name", None), []).append(candidate)
        return names

    def nodes_of_type(self, cls: Type[T]) -> List[T]:
        return [n for n in self.nodes.values() if isinstance(n, cls)]

    def class_named(self, name: str) -> Optional[Node]:
        plain = (name or "").strip()
        if not plain:
            return None
        for node in self.nodes.values():
            if node.name == plain and node.semantic_type() in _CLASS_SEMANTICS:
                return node
        return None

    def operation_named(self, class_name: str, operation_name: str) -> Optional[Node]:
        owner = self.class_named(class_name)
        if owner is None:
            wanted = (class_name or "").replace("\\", "/")
            for node in self.nodes.values():
                if node.semantic_type() != "File":
                    continue
                if node.name.replace("\\", "/") == wanted:
                    owner = node
                    break
        if owner is None:
            return None
        for node in owner.related(Kind.OWNS):
            if node.semantic_type() == "Operation" and node.name == operation_name:
                return node
        return None

    def find_class(self, name: str) -> Optional[Node]:
        return self.class_named(name)

    def find_operation(self, class_name: str, operation_name: str) -> Optional[Node]:
        return self.operation_named(class_name, operation_name)

    def outgoing_nodes(self, node: Node, kind: str) -> List[Node]:
        return node.related(kind)

    def incoming_nodes(self, node: Node, kind: str) -> List[Node]:
        return node.related(kind, direction="in")

    def index_module(self, module: Node) -> None:
        self.modules[module.name] = module

    def index_epic(self, epic: Node) -> None:
        self.epics[epic.name] = epic

    def index_description(self, description: Node) -> None:
        self.descriptions[description.name] = description

    def evaluate_rules(
        self,
        slugs: RuleSlugs | None = None,
        skip: RuleSlugs | None = None,
        *,
        codeql_results: str | Path | None = None,
        database: Path | None = None,
    ) -> Failures:
        wanted = set(slugs.names) if slugs is not None and slugs.names else None
        skipped = set(skip.names) if skip is not None and skip.names else None
        by_node = self._evaluate_graph_rules(
            slugs=wanted, skip=skipped, database=database
        )
        if wanted:
            self._merge_rule_hits(by_node, wanted)
        else:
            self._violations_by_node = by_node
        self._merge_codeql_violations(
            self._violations_by_node,
            Path(codeql_results) if codeql_results else None,
        )
        drop_cloned_operation_hits(self, self._violations_by_node)
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
            if item.slug.startswith("run-queries:") or item.slug.startswith(
                "decode-facts:"
            ):
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

    def record_rule_timing(self, timing: RuleTiming) -> None:
        self.rule_timings.append(timing)

    def _is_direct_violation(self, node: Node, violation: RuleViolation) -> bool:
        closest = closest_fidelity(node.practice, node.semantic_type())
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
            node = RuleViolation.from_entry(self, entry)
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

    def _evaluate_graph_rules(
        self,
        *,
        slugs: Optional[set] = None,
        skip: Optional[set] = None,
        database: Path | None = None,
    ) -> Dict[str, List[RuleViolation]]:
        from collections import defaultdict

        from .codeql import CodeQL, Rows

        by_node: Dict[str, List[RuleViolation]] = {}
        runnable, skipped_rules = self.rule_registry.runnable(slugs=slugs, skip=skip)
        self._record_skipped_rules(skipped_rules)
        by_pack = defaultdict(list)
        for rule in runnable:
            if rule.graphQuery is None and rule.pack_rules_query is None:
                continue
            by_pack[rule.query_pack].append(rule)
        codeql = CodeQL(self.root)
        self._codeql = codeql
        self._named = self.named_nodes()
        self._hits_by_node = by_node
        self._rule_database = database
        for pack, pack_rules in by_pack.items():
            self._pack = pack
            self._pack_rules = pack_rules
            self._evaluate_pack()
        return by_node

    def _record_skipped_rules(self, skipped_rules) -> None:
        for rule in skipped_rules:
            print(f"skip {rule.slug} (0 hits)", flush=True)
            self.record_rule_timing(RuleTiming(rule.slug, 0.0, 0, "skipped"))

    def _evaluate_pack(self) -> None:
        import time

        pack = self._pack
        pack_rules = self._pack_rules
        if not pack_rules:
            return
        database = self._rule_database or self._codeql._ready_database()
        if database is None:
            print(f"skip {pack.name} (no codeql database)", flush=True)
            return
        print(f"run-queries {pack.name} ({len(pack_rules)} rules) ...", flush=True)
        started = time.perf_counter()
        try:
            batch = self._rule_rows()
        except Exception as error:
            self._record_pack_error(started, error)
            return
        seconds = time.perf_counter() - started
        self.record_rule_timing(
            RuleTiming(
                f"run-queries:{pack.name}",
                seconds,
                sum(len(batch.get(rule.slug) or []) for rule in pack_rules),
            )
        )
        print(f"run-queries {pack.name}  {seconds:.2f}s", flush=True)
        self._map_pack_hits(batch)

    def _record_pack_error(self, started: float, error: Exception) -> None:
        import time

        pack = self._pack
        seconds = time.perf_counter() - started
        self.record_rule_timing(
            RuleTiming(
                f"run-queries:{pack.name}",
                seconds,
                0,
                f"{type(error).__name__}: {error}",
            )
        )
        self.record_partial_failure(f"run-queries {pack.name}", error)
        print(f"run-queries {pack.name}  {seconds:.2f}s  ERROR {error}", flush=True)

    def _map_pack_hits(self, batch) -> None:
        import time

        from .codeql import Rows

        for rule in self._pack_rules:
            print(f"rule {rule.slug} ...", flush=True)
            mapped = time.perf_counter()
            try:
                hits = rule.evaluate(
                    self,
                    hits=Rows.from_tuples(batch.get(rule.slug) or []),
                    by_name=self._named,
                )
            except Exception as error:
                elapsed = time.perf_counter() - mapped
                self.record_rule_timing(
                    RuleTiming(rule.slug, elapsed, 0, f"{type(error).__name__}: {error}")
                )
                self.record_partial_failure(f"rule {rule.slug}", error)
                print(f"rule {rule.slug}  {elapsed:.2f}s  ERROR {error}", flush=True)
                continue
            elapsed = time.perf_counter() - mapped
            self.record_rule_timing(RuleTiming(rule.slug, elapsed, len(hits)))
            print(f"rule {rule.slug}  {elapsed:.2f}s  hits={len(hits)}", flush=True)
            for violation in hits:
                self._hits_by_node.setdefault(violation.node_id, []).append(violation)

    def _rule_rows(self) -> Dict[str, list]:
        hits_lib = self._pack / "rule_hits.qll"
        self._combined_slugs = []
        self._leftover_queries = []
        for rule in self._pack_rules:
            self._collect_pack_query(rule, hits_lib)
        batch: Dict[str, list] = {}
        if self._combined_slugs:
            batch.update(self._combined_rule_rows())
        self._leftover_rule_rows(batch)
        return batch

    def _collect_pack_query(self, rule, hits_lib) -> None:
        if rule.graphQuery is None:
            return
        if not self._codeql.query_matches_pack(rule.graphQuery):
            print(
                f"skip {rule.slug} (query language does not match pack)",
                flush=True,
            )
            return
        if hits_lib.is_file():
            self._combined_slugs.append(rule.slug)
            return
        self._leftover_queries.append(rule.graphQuery)

    def _combined_rule_rows(self) -> Dict[str, list]:
        pack = self._pack
        combined = pack / "rules.ql"
        language = self._codeql.query_language(combined) if combined.is_file() else (
            self._codeql.pack_language(pack) or "python"
        )
        self._codeql.write_rules_query(pack)
        db = self._rule_database if self._rule_database is not None else self._codeql.ensure_database(language)
        return self._codeql.run_rules(pack / "rules.ql", self._combined_slugs, database=db)

    def _leftover_rule_rows(self, batch: Dict[str, list]) -> None:
        by_language: Dict[str, list] = {}
        for query in self._leftover_queries:
            language = self._codeql.query_language(query)
            by_language.setdefault(language, []).append(query)
        for language, queries in by_language.items():
            try:
                db = (
                    self._rule_database
                    if self._rule_database is not None
                    else self._codeql.ensure_database(language)
                )
                batch.update(self._codeql.run_queries(queries, database=db))
            except Exception as error:
                print(f"run-queries leftover/{language}  ERROR {error}", flush=True)

    @property
    def dot_graph(self) -> str:
        from .dot_graph import dot_graph_from_roots

        owned = {edge.to_id for edge in self.relationships if edge.kind == Kind.OWNS}
        roots = [node for node in self.nodes.values() if node.node_id not in owned]
        if not roots:
            return "digraph practice_graph {}\n"
        return dot_graph_from_roots(roots, graph_name="practice_graph")
