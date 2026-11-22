"""story_map fidelity — epic, sub-epic, and story rules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.stories.model import story_map
from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_VERB_OPENINGS = {"verb", "unlisted"}
# A generic verb is listed for the judgment to decide from its context, not failed on its own (stories.md).
_GENERIC_VERB = "generic-verb"


class VerbNounFormat(PracticeGraphRule):
    slug = "verb-noun-format"
    node_types = ("Epic", "SubEpic", "Story")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.has_fact("opening_class"):
            return []
        kind = node.get_fact("opening_class") or ""
        if kind in _VERB_OPENINGS:
            return []
        if kind == _GENERIC_VERB:
            return [Finding(node, f"{node.type} {node.name!r}: opens with a generic verb; judge from its context whether the action is plain.")]
        return [Finding(node, f"{node.type} {node.name!r}: name should start with a verb (got {kind}).")]


class ChildCountFitsLayer(PracticeGraphRule):
    """An epic or sub-epic holds the number of children its layer reads well: the band the story map model holds for
    a node that holds sub-epics, for a sub-epic, and for a top epic of stories (``LAYER_BANDS``). The node's map facts
    carry its count, its band's target, and whether the count is outside it."""

    slug = "child-count-fits-layer"
    node_types = ("Epic", "SubEpic")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        severity = node.get_fact("child_band") or ""
        if severity != "error":
            return []
        count = node.get_fact("child_count", 0)
        label = node.get_fact("child_label") or "children"
        target = node.get_fact("child_target")
        kind = node.type.lower().replace("subepic", "sub-epic")
        return [Finding(node, f"{kind} {node.name!r}: {count} {label} (target {target})")]


class StoryScenariosAtMostSeven(PracticeGraphRule):
    """Code scenarios on a story: at most the number the story map model holds (``MOST_SCENARIOS``). More and the story is huge. A story with none
    has not had its scenarios written yet, which is ordinary while the map is ahead of the scenarios."""

    slug = "story-scenarios-at-most-seven"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        count = node.get_fact("scenario_count")
        if count is None and (node.get_fact("child_label") or "") == "scenarios":
            count = node.get_fact("child_count", 0)
        if count is None:
            return []
        count = int(count)
        if count <= story_map.MOST_SCENARIOS:
            return []
        return [Finding(node, f"story {node.name!r}: {count} scenarios — story is huge (target 1-{story_map.MOST_SCENARIOS})")]


class KebabCasePaths(PracticeGraphRule):
    """A story judges the file it was read from: its story test, or the story map that lists it."""

    slug = "kebab-case-paths"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.get_fact("camel_case_path"):
            return []
        name = node.get_fact("artifact_name") or ""
        return [Finding(node, f"Story artifact '{name}' should use kebab-case in the file name.")]


class StoryNameCapturesSystemMechanic(PracticeGraphRule):
    slug = "story-name-captures-system-mechanic"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.get_fact("generic_handler"):
            return []
        return [Finding(node, f"Story {node.name!r} names a generic handler; use the system mechanic (e.g. 'Submit Order').")]


class RightSizeStoryNodes(PracticeGraphRule):
    """Sibling stories should be distinct intents, not typos or duplicates."""

    slug = "right-size-story-nodes"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.get_fact("near_duplicate"):
            return []
        return [Finding(node, f"Story {node.name!r} is too similar to another story on the same map node.")]


class BranchOnMechanicalUniqueness(PracticeGraphRule):
    """An epic or sub-epic judges the stories under it, which share a verb when one mechanic was split into many."""

    slug = "branch-on-mechanical-uniqueness"
    node_types = ("Epic", "SubEpic")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        verb = node.get_fact("shared_verb") or ""
        if not verb:
            return []
        return [Finding(node, f"Stories under {node.name!r} share the same verb {verb!r}; split by distinct mechanics or merge.")]


