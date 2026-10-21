"""story_map fidelity — epic, sub-epic, and story rules."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

_EVIDENCE = {"observed", "inferred", "intended"}


class VerbNounFormat(PracticeGraphRule):
    slug = "verb-noun-format"
    node_types = ("Epic", "SubEpic", "Story")

    def check(self, node, context) -> list[str]:
        if "opening_class" not in node.data:
            return []
        kind = node.data.get("opening_class") or ""
        if kind == "verb":
            return []
        return [f"{node.type} {node.name!r}: name should start with a verb (got {kind})."]


class FourToNineChildren(PracticeGraphRule):
    slug = "four-to-nine-children"
    node_types = ("Epic", "SubEpic")

    def check(self, node, context) -> list[str]:
        if node.type in {"Story", "Scenario"}:
            return []
        severity = node.data.get("child_band") or ""
        if severity not in {"warning", "error"}:
            return []
        count = node.data.get("child_count", 0)
        label = node.data.get("child_label") or "children"
        kind = node.type.lower().replace("subepic", "sub-epic")
        return [f"{kind} {node.name!r}: {count} {label} (target 4-9)"]


class StoryScenariosOneToFour(PracticeGraphRule):
    """Code scenarios on a story: 1 to 4. More than four and the story is huge."""

    slug = "story-scenarios-one-to-four"
    node_types = ("Story",)

    def check(self, node, context) -> list[str]:
        count = node.data.get("scenario_count")
        if count is None and (node.data.get("child_label") or "") == "scenarios":
            count = node.data.get("child_count", 0)
        if count is None:
            return []
        count = int(count)
        if 1 <= count <= 4:
            return []
        if count > 4:
            return [f"story {node.name!r}: {count} scenarios — story is huge (target 1-4)"]
        return [f"story {node.name!r}: {count} scenarios (target 1-4)"]


class KebabCasePaths(PracticeGraphRule):
    slug = "kebab-case-paths"
    node_types = ("Story", "Scenario", "Epic", "SubEpic")

    def check(self, node, context) -> list[str]:
        if not node.data.get("camel_case_path"):
            return []
        name = node.data.get("artifact_name") or ""
        return [f"Story artifact '{name}' should use kebab-case in the file name."]


class StoryNameCapturesSystemMechanic(PracticeGraphRule):
    slug = "story-name-captures-system-mechanic"
    node_types = ("Story",)

    def check(self, node, context) -> list[str]:
        if not node.data.get("generic_handler"):
            return []
        return [
            f"Story {node.name!r} names a generic handler; use the system mechanic (e.g. 'Submit Order')."
        ]


class RightSizeStoryNodes(PracticeGraphRule):
    """Sibling stories should be distinct intents, not typos or duplicates."""

    slug = "right-size-story-nodes"
    node_types = ("Story",)

    def check(self, node, context) -> list[str]:
        if not node.data.get("near_duplicate"):
            return []
        return [f"Story {node.name!r} is too similar to another story on the same map node."]


class BranchOnMechanicalUniqueness(PracticeGraphRule):
    slug = "branch-on-mechanical-uniqueness"
    node_types = ("Epic", "SubEpic", "Story")

    def check(self, node, context) -> list[str]:
        verb = node.data.get("shared_verb") or ""
        if not verb:
            return []
        return [
            f"Stories under {node.name!r} share the same verb {verb!r}; split by distinct mechanics or merge."
        ]


class BehavioursNotOneTimeTasks(PracticeGraphRule):
    slug = "behaviours-not-one-time-tasks"
    node_types = ("Story",)

    def check(self, node, context) -> list[str]:
        if not node.data.get("one_time_task"):
            return []
        return [f"Story {node.name!r} reads like a one-time task, not a repeatable behaviour."]


class EvidenceDistinguishesObservedInferredAndIntended(PracticeGraphRule):
    slug = "evidence-distinguishes-observed-inferred-and-intended"
    node_types = ("Epic", "SubEpic", "Story")

    def check(self, node, context) -> list[str]:
        labels = node.data.get("evidence") or []
        if isinstance(labels, str):
            labels = [labels]
        if any(str(item).strip().casefold() in _EVIDENCE for item in labels):
            return []
        kind = node.type.lower().replace("subepic", "sub-epic")
        return [f"{kind} {node.name!r}: evidence must be observed, inferred, or intended."]
