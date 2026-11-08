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
        practice = graph.practice_of(practice_class)
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
    """One rule run over one practice's nodes the way the graph runs it in validate: the practice's schema says which
    node types carry the rule, so a hit on a node whose type does not list the rule is dropped, and a check runs only
    on the nodes whose rules say it runs there. A rule the schema never applies finds nothing, so its spec fails."""

    def __init__(self, rule, context: RuleCheckContext) -> None:
        self.rule = rule
        self.context = context

    def hits(self) -> list[str]:
        """Each message the rule reports over the whole practice on a node that carries it, then on each node whose
        rules run it."""
        slug, context = self.rule.slug, self.context
        messages = [message for node_id, message in self.rule.check_practice(context) if self._carries(context.node(node_id))]
        for node in context.nodes():
            entry = node.rules.entries.get(slug)
            if entry is not None and entry.runs:
                messages.extend(self.rule.check(node, context))
        return messages

    def node_hits(self, node) -> list[str]:
        """The messages the rule reports on node alone, when node's rules run it."""
        entry = node.rules.entries.get(self.rule.slug)
        return list(self.rule.check(node, self.context)) if entry is not None and entry.runs else []

    def _carries(self, node) -> bool:
        return node is not None and self.rule.slug in node.rules.slugs


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
