"""LERN story-file rules — read the facts recorded on each LERN story file node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class TierBoundRepositoryAccessor(PracticeGraphRule):
    """Shared stories reach repositories through the accessor each tier binds, not by casting `ctx`."""

    slug = "tier-bound-repository-accessor"
    node_types = ("StoryShared",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{node.source.file}:{line}: `{cast}` casts the story context; "
            f"read the repository through the tier-bound `repositories` accessor.")
            for line, cast in node.get_fact("context_casts", [])
        ]


class NoExpectInGiven(PracticeGraphRule):
    """A Given sets up state; checking it is a Then's job."""

    slug = "no-expect-in-given"
    node_types = ("StoryShared",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{node.source.file}:{line}: Given {name!r} asserts; move the check to a Then or drop it.")
            for line, name in node.get_fact("asserting_givens", [])
        ]


class DomainOperationsInlineInSteps(PracticeGraphRule):
    """A story-file helper that reaches the repositories hides the domain operation its steps run."""

    slug = "domain-operations-inline-in-steps"
    node_types = ("StoryShared", "DomainSpec", "ServerSpec", "PlaywrightSpec")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{node.source.file}:{line}: `{helper}` wraps domain operations ({', '.join(calls)}); call them in the "
            f"step that relies on them, or seed the state with a fixture in the examples file.")
            for line, helper, calls in node.get_fact("domain_wrapping_helpers", [])
        ]


class OutlineEntriesLoopOverExamples(PracticeGraphRule):
    """`scenario('Outline: entry', …)` with a fixed string is one outline example entry written by hand."""

    slug = "outline-entries-loop-over-examples"
    node_types = ("StoryShared", "PlaywrightSpec")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{node.source.file}:{line}: scenario {outline!r} entry {entry!r} is written by hand; "
            f"loop over the outline's examples export instead.")
            for line, outline, entry in node.get_fact("hand_written_entries", [])
        ]


class PlaywrightTestsBrowserInteraction(PracticeGraphRule):
    """Every story has a screen story: a Playwright file whose describe names it drives the page the domain and server
    specs cannot see. Validate keeps only the stories the session's ticket names. The overlay's read keeps on each story
    whether one names it (``has_screen_story``)."""

    slug = "playwright-tests-browser-interaction"
    node_types = ("Story",)

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(story, f"{story.source.file}: story `{story.name}` has no screen story: no Playwright file "
                            f"(`*.story.ui.spec.ts`) has a describe named for it; write one that drives its screen.")
            for story in context.nodes("Story")
            if not story.get_fact("has_screen_story")
        ]
