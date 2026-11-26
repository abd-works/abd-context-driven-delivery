"""TDD's graph rules shared across the practices it supplements: each binds to the node types of the practices it
names, and reads one fact TDD's overlay recorded on the node (``graph_overlay.py``). A rule the graph cannot see, such
as suffix-names-the-tier (a file no tier names is never read as a test), stays a rule validate judges."""
from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.stories.stories import Stories
from harness.graph.practice_rule import SCOPE_ALL, SharedPracticeGraphRule
from harness.graph.violation import Finding

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class UnitTierFakesEveryBoundary(SharedPracticeGraphRule):
    """A unit test that reaches a real process, socket, or browser is slow and flaky; fake the boundary there and cover
    the real one in a heavy test."""

    slug = "unit-tier-fakes-every-boundary"
    node_types_by_practice = {Bdd: ("Spec",), Stories: ("Story",)}

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{node.source.file}:{line}: a unit test imports {module}; put a fake at that boundary and cover the real "
            f"one in a heavy test.")
            for line, module in node.get_fact("real_resources", [])
        ]


class OperationHasAProvingTest(SharedPracticeGraphRule):
    """A public operation with a body that no test the graph read reaches: no observation or step invokes it, no test
    code calls it, none of the ways the project names in its config reaches it (``source_code/code_reach.py``), and no operation a test reaches goes
    on to invoke it. It requires a judge, because the links a load finds miss a call made by a name the code builds,
    such as a test that loads a module by a path, or a call from another language, so each operation it lists is a candidate to read. A graph that read no test records nothing to judge."""

    slug = "operation-has-a-proving-test"
    scope = SCOPE_ALL
    requires_judge = True
    node_types_by_practice = {CleanEngineering: ("Operation",)}

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.has_fact("reached_by_a_test") or node.get_fact("reached_by_a_test"):
            return []
        return [Finding(node, f"No observation or step reaches the public operation {node.name!r}, directly or through an operation it "
            "invokes: add a test that invokes it.")]


class DeclaredExceptionRaisedByATest(SharedPracticeGraphRule):
    """An exception class production code declares whose name no test file or test code writes, so no test expects it
    raised. A graph that read no test records nothing to judge."""

    slug = "declared-exception-raised-by-a-test"
    scope = SCOPE_ALL
    node_types_by_practice = {CleanEngineering: ("OoadClass",)}

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.has_fact("named_by_a_test") or node.get_fact("named_by_a_test"):
            return []
        return [Finding(node, f"No test names the exception {node.name!r}, so no test sees it raised: add a test that breaks its invariant "
            "and expects it.")]


class StubbedBoundaryHasHeavyCoverage(SharedPracticeGraphRule):
    """A unit spec that stubs a boundary while no heavy or e2e spec has any of its should sentences under its subject:
    nothing then runs that boundary for real, so the stub can drift from the thing it stands for. It requires a judge:
    the graph sees that a spec puts a stand-in somewhere (a mock, a patch, a spy, a class named as a fake) but not
    whether that place is an architecture boundary, and a heavy example worded another way covers it unseen."""

    slug = "stubbed-boundary-has-heavy-coverage"
    requires_judge = True
    node_types_by_practice = {Bdd: ("Spec",)}

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        stubs = node.get_fact("stubbed_boundaries", [])
        if not stubs or node.get_fact("heavy_examples", 0):
            return []
        line, stub = stubs[0]
        return [Finding(node, f"{node.source.file}:{line}: a unit spec stubs a boundary with {stub}, and no heavy or e2e example has one of "
            f"its `should` sentences under the subject {node.get_fact('subject', '')!r}: run that boundary for real in one.")]


RULES: tuple = (UnitTierFakesEveryBoundary(), OperationHasAProvingTest(), DeclaredExceptionRaisedByATest(), StubbedBoundaryHasHeavyCoverage())
BY_SLUG = {rule.slug: rule for rule in RULES}
