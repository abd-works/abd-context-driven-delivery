"""TDD's graph rules shared across the practices it supplements: each binds to the node types of the practices it
names. A rule the graph cannot see, such as suffix-names-the-tier (a file no tier names is never read as a test),
stays a rule validate judges."""
from __future__ import annotations

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.stories.stories import Stories
from harness.graph.practice_rule import SharedPracticeGraphRule


class UnitTierFakesEveryBoundary(SharedPracticeGraphRule):
    """A unit test that reaches a real process, socket, or browser is slow and flaky; fake the boundary there and cover
    the real one in a heavy test."""

    slug = "unit-tier-fakes-every-boundary"
    node_types_by_practice = {Bdd: ("Spec",), Stories: ("Story",)}

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: a unit test imports {module}; put a fake at that boundary and cover the real "
            f"one in a heavy test."
            for line, module in node.get_fact("real_resources", [])
        ]


RULES: tuple = (UnitTierFakesEveryBoundary(),)
BY_SLUG = {rule.slug: rule for rule in RULES}
