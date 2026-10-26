"""LERN shared-story rules — read the facts recorded on each `*.story.shared.ts` node."""

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
