"""A graph rule that requires a judge lists candidates for a judge or a person to read; a rule that does not is checked,
and what it finds is an error."""

import json
from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph, Node, Source
from harness.graph.graph_rules_collection import GraphRule
from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.saved_graph import NodeIdentity, SavedGraph
from harness.graph.violation import Finding, Violation
from harness.installation.data_class import data_of
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_SLUG = "limit-operation-parameters"
_MESSAGE = "Operation 'place' may name a gesture, not what the person means to do."


class _CountedRule(PracticeGraphRule):
    slug = _SLUG
    node_types = ("Operation",)


class _ReadRule(_CountedRule):
    requires_judge = True


def _operation_ruled_by(check: PracticeGraphRule) -> Node:
    """An operation whose rule is run by check, which has found one thing on it."""
    graph = Graph()
    graph.reads.open(Path("."))
    practice = graph.practices.named("clean_engineering")
    place = Node(practice, NodeIdentity(type="Operation", node_id="clean_engineering:Operation:place", name="place"), Source("order.py", 1, 2))
    place.rules.entries[_SLUG] = GraphRule(place, _SLUG, check)
    place.rules.entries[_SLUG].record(Finding(place, _MESSAGE))
    return place


with description("a graph rule's finding on a node"):
    with context("of a rule a program decides"):
        with before.each:
            self.rule = _operation_ruled_by(_CountedRule()).rules[_SLUG]

        with it("should say the rule is violating"):
            expect(self.rule.status).to(equal("violating"))

        with it("should say the rule requires no judge"):
            expect(data_of(self.rule)["requires_judge"]).to(be_false)

        with it("should be an error"):
            expect(self.rule.violations[0].severity).to(equal("error"))

    with context("of a rule that requires a judge"):
        with before.each:
            self.place = _operation_ruled_by(_ReadRule())
            self.rule = self.place.rules[_SLUG]

        with it("should say the rule has a candidate"):
            expect(self.rule.status).to(equal("candidate"))

        with it("should say the rule requires a judge"):
            expect(data_of(self.rule)["requires_judge"]).to(be_true)

        with it("should be a candidate, not an error"):
            expect(self.rule.violations[0].severity).to(equal("candidate"))

        with it("should stay a candidate when read back from the data a saved graph keeps"):
            expect(Violation.from_data(data_of(self.rule.violations[0])).severity).to(equal("candidate"))

        with it("should be kept by a graph made from the nodes a query returned"):
            returned = [{"practice": "clean_engineering", "rules": [data_of(self.rule)]}]
            kept = SavedGraph.from_text(json.dumps(returned)).violations()
            expect([violation.severity for violation in kept]).to(equal(["candidate"]))

        with it("should still be found by a filter that asks for the nodes with findings"):
            expect(self.place.failed_rules).to(equal([_SLUG]))

    with context("of a rule a program decides, that lists one finding for a judge"):
        with before.each:
            self.place = _operation_ruled_by(_CountedRule())
            self.rule = self.place.rules[_SLUG]
            self.rule.record(Finding(self.place, "Operations 'place' and 'put' may do the same work.", candidate=True))

        with it("should keep the finding the program decided an error"):
            expect(self.rule.violations[0].severity).to(equal("error"))

        with it("should keep the finding it lists for a judge a candidate"):
            expect(self.rule.violations[1].severity).to(equal("candidate"))

        with it("should keep the candidate a candidate when its node's rule takes it back from a saved graph"):
            restored = GraphRule(self.place, _SLUG, _CountedRule())
            restored.restore(Violation.from_data(data_of(self.rule.violations[1])))
            expect(restored.violations[0].severity).to(equal("candidate"))

        with it("should say the rule is violating while one finding is an error"):
            expect(self.rule.status).to(equal("violating"))

    with context("of a rule a program decides, that only lists findings for a judge on a node"):
        with it("should say the rule has a candidate there"):
            practice = _operation_ruled_by(_CountedRule()).practice
            checked = Node(practice, NodeIdentity(type="Operation", node_id="clean_engineering:Operation:put", name="put"), Source("order.py", 3, 4))
            checked.rules.entries[_SLUG] = GraphRule(checked, _SLUG, _CountedRule())
            checked.rules.entries[_SLUG].record(Finding(checked, "Operations 'put' and 'place' may do the same work.", candidate=True))
            expect(checked.rules[_SLUG].status).to(equal("candidate"))
