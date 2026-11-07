"""PracticeChecks. Run a practice's graph rules and record each violation on the node it was found on.

A practice names the graph rules it checks itself (``PracticeGuidance.graph_checks``), with the rules each pattern overlay
its graph applies adds to it (``PracticeGuidance.checks``). Which of them apply to one node, the node says itself
(``Node.rules``)."""

from __future__ import annotations

from pathlib import Path

from harness.graph.rule_context import RuleCheckContext


class PracticeChecks:
    """Every check one practice runs on the graph that holds it: over the whole practice, then node by node."""

    def __init__(self, practice) -> None:
        self.practice = practice
        self.graph = practice.graph
        source_root = self.graph.source_root_of(practice)
        self.context = RuleCheckContext(practice, Path(source_root) if source_root else None)

    def run(self) -> None:
        checks = list(self.practice.checks().values())
        if not checks:
            return
        for index, check in enumerate(checks, start=1):
            self._report(f"{self.practice.key} · rule {check.slug} · {index}/{len(checks)}")
            for node_id, message in check.check_practice(self.context):
                node = self.graph.node(node_id)
                if node is not None:
                    node.rules.record_violation(check.slug, message)
        self._check_each_node()

    def _check_each_node(self) -> None:
        """A node another practice's class covers skips that practice's checks, which already ran on the class."""
        covering = self._covering_classes()
        nodes = self.graph.nodes_of(self.practice)
        for index, node in enumerate(nodes, start=1):
            self._report(f"{self.practice.key} · rules · {index}/{len(nodes)} · {node.type} {node.name}")
            skipped = {slug for slugs, spans in covering for slug in slugs if self._inside(node, spans)}
            for rule in node.rules:
                if not rule.runs or rule.slug in skipped:
                    continue
                self._report(f"{self.practice.key} · rule {rule.slug} · {index}/{len(nodes)} · {node.name}")
                for message in rule.check(node, self.context):
                    node.rules.record_violation(rule.slug, message)

    def _covering_classes(self) -> list[tuple[frozenset[str], dict[str, list[tuple[int, int]]]]]:
        """For each other loaded practice that checks whole classes: its check slugs, and its classes' line spans by file."""
        found = []
        for other in self.graph.practices.values():
            class_type = other.class_node_type
            if other is self.practice or not class_type:
                continue
            spans: dict[str, list[tuple[int, int]]] = {}
            for node in self.graph.nodes_of(other, class_type):
                if node.source.file:
                    spans.setdefault(node.source.file.replace("\\", "/"), []).append((node.source.start_line, node.source.end_line))
            found.append((frozenset(other.checks()), spans))
        return found

    def _inside(self, node, spans: dict[str, list[tuple[int, int]]]) -> bool:
        file = (node.source.file or "").replace("\\", "/")
        start, end = node.source.start_line, node.source.end_line
        return any(start <= class_end and class_start <= end for class_start, class_end in spans.get(file, ()))

    def _report(self, message: str) -> None:
        self.graph.report_progress(message)
