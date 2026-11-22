"""A graph rule's scope: a rule of scope ``all`` runs over the graph of the whole working copy, so a validate reports
what it finds wherever it is, marked when it is outside the paths the validate was given; a rule of the default scope,
``paths``, reports only what it finds in those paths. A judged rule of scope ``all`` lists its candidates inside those paths
on every validate, as a rule of scope ``paths`` does, and over the rest of the working copy only when the validate asks
for the judged pass, since reading every candidate in a repository is work a person chooses to start."""

from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph, Node, Source
from harness.graph.graph_rules_collection import GraphRule
from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.saved_graph import NodeIdentity, SavedFiles
from harness.graph.violation import Finding, Violation
from harness.installation.data_class import data_of
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_SLUG = "limit-operation-parameters"
# The paths a validate was given, and a file outside them.
_GIVEN = ["src/orders"]
_ELSEWHERE = "src/billing/invoice.py"


class _PathsRule(PracticeGraphRule):
    slug = _SLUG
    node_types = ("Operation",)


class _WholeRule(_PathsRule):
    scope = "all"


class _JudgedWholeRule(_WholeRule):
    requires_judge = True


def _operation_in(file: str, check: PracticeGraphRule) -> Node:
    """An operation read from file whose rule is run by check, which has found one thing on it."""
    graph = Graph()
    graph.reads.open(Path("."))
    practice = graph.practices.named("clean_engineering")
    operation = Node(practice, NodeIdentity(type="Operation", node_id=f"clean_engineering:Operation:{file}:bill", name="bill"), Source(file, 1, 2))
    operation.rules.entries[_SLUG] = GraphRule(operation, _SLUG, check)
    operation.rules.entries[_SLUG].record(Finding(operation, "Operation 'bill' takes six parameters."))
    return operation


def _found(file: str, check: PracticeGraphRule) -> Violation:
    return _operation_in(file, check).rules[_SLUG].violations[0]


with description("a graph rule's scope") as self:
    with context("left as it is"):
        with it("should be the paths a validate was given"):
            expect(data_of(_operation_in(_ELSEWHERE, _PathsRule()).rules[_SLUG])["scope"]).to(equal("paths"))

        with it("should not report a violation outside those paths"):
            expect(_found(_ELSEWHERE, _PathsRule()).is_reported_for(_GIVEN, judge_all=False)).to(be_false)

        with it("should report a violation inside those paths"):
            expect(_found("src/orders/order.py", _PathsRule()).is_reported_for(_GIVEN, judge_all=False)).to(be_true)

        with it("should not keep the node of a violation outside those paths in the graph a validate checks"):
            expect(SavedFiles(_GIVEN).keeps_node(_operation_in(_ELSEWHERE, _PathsRule()))).to(be_false)

    with context("declared all, the whole working copy"):
        with before.each:
            self.operation = _operation_in(_ELSEWHERE, _WholeRule())
            self.found = self.operation.rules[_SLUG].violations[0]

        with it("should say so on the rule"):
            expect(data_of(self.operation.rules[_SLUG])["scope"]).to(equal("all"))

        with it("should say so on each violation, as the data a saved graph keeps"):
            expect(Violation.from_data(data_of(self.found)).runs_over_all).to(be_true)

        with it("should report a violation outside the paths a validate was given"):
            expect(self.found.is_reported_for(_GIVEN, judge_all=False)).to(be_true)

        with it("should keep the node of that violation in the graph a validate checks"):
            expect(SavedFiles(_GIVEN).keeps_node(self.operation)).to(be_true)

    with context("declared all, of a rule that requires a judge"):
        with before.each:
            self.inside = _found("src/orders/order.py", _JudgedWholeRule())
            self.outside = _found(_ELSEWHERE, _JudgedWholeRule())

        with it("should list its candidate inside the paths a validate was given, as every validate does"):
            expect(self.inside.is_reported_for(_GIVEN, judge_all=False)).to(be_true)

        with it("should not list its candidate outside those paths when the validate does not ask for the judged pass"):
            expect(self.outside.is_reported_for(_GIVEN, judge_all=False)).to(be_false)

        with it("should list its candidate outside those paths when the validate asks for the judged pass"):
            expect(self.outside.is_reported_for(_GIVEN, judge_all=True)).to(be_true)

    with context("left as it is, of a rule that requires a judge"):
        with it("should list its candidate inside the paths without the judged pass, as it does today"):
            class _Judged(_PathsRule):
                requires_judge = True

            expect(_found("src/orders/order.py", _Judged()).is_reported_for(_GIVEN, judge_all=False)).to(be_true)
