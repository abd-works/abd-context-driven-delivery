"""Spec support for graph rules: a small tree of fixture files read through the real working-copy build, and the hits
one graph rule finds in it. Every practice's rule specs check a rule this one way."""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext


class RuleFixture:
    """Fixture files written to a folder of their own and read by one practice, the way a live load reads a working
    copy: its language model parses each file and every node loads its own facts. The fixture keeps the folder, which
    goes when the fixture does."""

    def __init__(self, practice_class: type, files: dict[str, str]) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        for relative, text in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        graph = Graph()
        practice = graph.practice_of(practice_class)
        graph.load_working_copy(str(self.root), {practice.key: str(self.root)}, force=True)
        self.practice = practice

    def read_only(self, paths: list[str]) -> None:
        """Read again only the files or folders at paths, as a load of the files being edited does."""
        self.practice.graph.load_files(str(self.root), [self.practice.key], paths)

    @property
    def context(self) -> RuleCheckContext:
        """What a rule check reads: this fixture's practice and folder."""
        return RuleCheckContext(self.practice, self.root)

    def hits(self, rule) -> list[str]:
        """Each message the rule reports: over the whole practice, then on each node of the types it checks."""
        context = self.context
        messages = [message for _node_id, message in rule.check_practice(context)]
        for node_type in rule.node_types:
            for node in context.nodes(node_type):
                messages.extend(rule.check(node, context))
        return messages


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
