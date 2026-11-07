"""PracticeChecks. Run a practice's graph rules and record each violation on the node it was found on."""

from __future__ import annotations

from pathlib import Path

from harness.graph.graph_practice import GraphPractices
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_rules import PracticeSchema


class PracticeChecks:
    """Every check one practice graph runs: over the whole practice, then node by node."""

    def __init__(self, practice) -> None:
        self.practice = practice
        self.patterns = practice.graph.overlay_patterns if practice.graph is not None else ()
        self.graph_practice = GraphPractices.named(practice.name)
        self.context = RuleCheckContext(practice, Path(practice.source_root) if practice.source_root else None)

    def run(self) -> None:
        PracticeSchema.load(self.practice.name, self.patterns).apply_to(self.practice)
        checks = list(self.graph_practice.checks(self.patterns).values())
        if not checks:
            return
        for index, check in enumerate(checks, start=1):
            self._report(f"{self.practice.name} · rule {check.slug} · {index}/{len(checks)}")
            for node_id, message in check.check_practice(self.context):
                node = self.practice.registered(node_id)
                if node is not None:
                    node.rules.record_violation(check.slug, message)
        self._check_each_node()

    def _check_each_node(self) -> None:
        """A node another practice's class covers skips that practice's checks, which already ran on the class."""
        covering = self._covering_classes()
        nodes = [node for group in self.practice.nodes.values() for node in group]
        for index, node in enumerate(nodes, start=1):
            self._report(f"{self.practice.name} · rules · {index}/{len(nodes)} · {node.type} {node.name}")
            skipped = {slug for slugs, spans in covering for slug in slugs if self._inside(node, spans)}
            for check in self.graph_practice.checks_for(node, self.patterns).values():
                if check.slug not in node.rules.slugs or check.slug in skipped:
                    continue
                self._report(f"{self.practice.name} · rule {check.slug} · {index}/{len(nodes)} · {node.name}")
                for message in check.check(node, self.context):
                    node.rules.record_violation(check.slug, message)

    def _covering_classes(self) -> list[tuple[frozenset[str], dict[str, list[tuple[int, int]]]]]:
        """For each other loaded practice that checks whole classes: its check slugs, and its classes' line spans by file."""
        graph = self.practice.graph
        if graph is None:
            return []
        found = []
        for name, other in graph.practices.items():
            class_type = GraphPractices.named(name).class_node_type
            if name == self.practice.name or not class_type:
                continue
            spans: dict[str, list[tuple[int, int]]] = {}
            for node in other.nodes.get(class_type, []):
                if node.source.file:
                    spans.setdefault(node.source.file.replace("\\", "/"), []).append((node.source.start_line, node.source.end_line))
            found.append((frozenset(GraphPractices.named(name).checks()), spans))
        return found

    def _inside(self, node, spans: dict[str, list[tuple[int, int]]]) -> bool:
        file = (node.source.file or "").replace("\\", "/")
        start, end = node.source.start_line, node.source.end_line
        return any(start <= class_end and class_start <= end for class_start, class_end in spans.get(file, ()))

    def _report(self, message: str) -> None:
        if self.practice.graph is not None:
            self.practice.graph.report_progress(message)
