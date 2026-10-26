"""LERN story-file rules — read the facts recorded on each LERN story file node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class TierBoundRepositoryAccessor(PracticeGraphRule):
    """Shared stories reach repositories through the accessor each tier binds, not by casting `ctx`."""

    slug = "tier-bound-repository-accessor"
    node_types = ("StoryShared",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{cast}` casts the story context; "
            f"read the repository through the tier-bound `repositories` accessor."
            for line, cast in node.get_fact("context_casts", [])
        ]


class NoExpectInGiven(PracticeGraphRule):
    """A Given sets up state; checking it is a Then's job."""

    slug = "no-expect-in-given"
    node_types = ("StoryShared",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: Given {name!r} asserts; move the check to a Then or drop it."
            for line, name in node.get_fact("asserting_givens", [])
        ]


class DomainOperationsInlineInSteps(PracticeGraphRule):
    """A story-file helper that reaches the repositories hides the domain operation its steps run."""

    slug = "domain-operations-inline-in-steps"
    node_types = ("StoryShared", "DomainSpec", "ServerSpec", "PlaywrightSpec")

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{helper}` wraps domain operations ({', '.join(calls)}); call them in the "
            f"step that relies on them, or seed the state with a fixture in the examples file."
            for line, helper, calls in node.get_fact("domain_wrapping_helpers", [])
        ]


class OutlineRowsLoopOverExamples(PracticeGraphRule):
    """`scenario('Outline: row', …)` with a fixed string is one outline row written by hand."""

    slug = "outline-rows-loop-over-examples"
    node_types = ("StoryShared", "PlaywrightSpec")

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: scenario {outline!r} row {row!r} is written by hand; "
            f"loop over the outline's examples export instead."
            for line, outline, row in node.get_fact("hand_written_rows", [])
        ]
