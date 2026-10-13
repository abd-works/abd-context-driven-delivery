"""Story graph rules — verb-noun-format (ported from stories/scanners discovery behavior)."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_true, equal, expect
from mamba import before, context, description, it

from graph import Node, PracticeGraph, Source
from harness.graph.rule_context import RuleCheckContext
from practices.stories.rules.verb_noun_format import VerbNounFormat


def _story(name: str, practice: PracticeGraph) -> Node:
    node = Node(
        practice,
        "Story",
        f"stories:Story:map.{name.replace(' ', '_')}",
        name,
        Source("story-map.md", 1, 1),
    )
    practice.by_id[node.node_id] = node
    practice.nodes.setdefault("Story", []).append(node)
    return node


with description("verb-noun-format graph rule"):
    with before.each:
        self.practice = PracticeGraph("stories")
        self.rule = VerbNounFormat()
        self.context = RuleCheckContext(self.practice, Path("."))

    with context("a story name that starts with a verb"):
        with it("should produce no violations"):
            node = _story("Submit order", self.practice)
            expect(self.rule.check(node, self.context)).to(equal([]))

    with context("a story name that starts with an actor noun"):
        with it("should report a violation"):
            node = _story("Customer submits order", self.practice)
            hits = self.rule.check(node, self.context)
            expect(len(hits) >= 1).to(be_true)
