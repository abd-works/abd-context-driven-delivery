"""Spec support for graph rules: a small tree of fixture files read through the real working-copy build, and the hits
one graph rule finds in it. Every practice's rule specs check a rule this one way."""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext


class RuleFixture:
    """Fixture files written to a folder of their own and read by one practice, the way a live load reads a working
    copy: its language model parses each file and every node loads its own facts. A practice that extends another,
    such as DDD reading Clean Engineering's classes, is read with that practice, as a live load reads them. The fixture
    keeps the folder, which goes when the fixture does."""

    def __init__(self, practice_class: type, files: dict[str, str]) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        for relative, text in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        graph = Graph()
        practice = graph.practices.of(practice_class)
        read = [practice, *([practice.extended] if practice.extended is not None else [])]
        graph.load_working_copy(str(self.root), {each.key: str(self.root) for each in read}, force=True)
        self.practice = practice

    def read_only(self, paths: list[str]) -> None:
        """Read again only the files or folders at paths, as a load of the files being edited does."""
        self.practice.graph.load_files(str(self.root), [self.practice.key], paths)

    @property
    def context(self) -> RuleCheckContext:
        """What a rule check reads: this fixture's practice and folder."""
        return RuleCheckContext(self.practice, self.root)

    def hits(self, rule) -> list[str]:
        """Each message the rule reports where validate keeps it."""
        return SchemaRuleRun(rule, self.context).hits()


class SchemaRuleRun:
    """One rule's findings over one practice's nodes, as the graph's own check records them when validate runs it
    (``InGraph.check``): the practice's schema says which node types carry the rule, a check runs only on the nodes
    whose rules say it runs there, and a node another practice's class covers skips that practice's checks. The check
    runs every rule the practice checks, so the nodes a spec adds after the load are checked as a load checks its own;
    a finding is kept once. A rule the practice does not check, or the schema never applies, finds nothing, so its
    spec fails."""

    def __init__(self, rule, context: RuleCheckContext) -> None:
        self.rule = rule
        self.context = context

    def hits(self) -> list[str]:
        """Each message the rule recorded, node by node, after the graph has checked the practice."""
        self.context.practice.in_graph.rule_run.check()
        return [message for node in self.context.nodes() for message in self._recorded_on(node)]

    def node_hits(self, node) -> list[str]:
        """The messages the rule recorded on node alone, after the graph has checked the practice."""
        self.context.practice.in_graph.rule_run.check()
        return self._recorded_on(node)

    def _recorded_on(self, node) -> list[str]:
        entry = node.rules.entries.get(self.rule.slug)
        return [violation.message for violation in getattr(entry, "violations", [])]


class RulePair:
    """A rule's failing fixture and its repaired fixture: the rule must flag the first and pass the second."""

    def __init__(self, rule, faulty: RuleFixture, repaired: RuleFixture) -> None:
        self.rule = rule
        self.faulty = faulty
        self.repaired = repaired

    def check(self) -> None:
        """Raise AssertionError when the rule finds nothing in the failing fixture, or anything in the repaired one."""
        if not self.faulty.hits(self.rule):
            raise AssertionError(f"{self.rule.slug}: expected violations on the failing fixture, got none")
        repaired_hits = self.repaired.hits(self.rule)
        if repaired_hits:
            raise AssertionError(f"{self.rule.slug}: expected no violations on the repaired fixture, got {repaired_hits!r}")
