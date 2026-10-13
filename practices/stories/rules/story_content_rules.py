"""Story / step content rules ported from TypeScript example fixtures."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_GENERIC_STORY = re.compile(
    r"^(Handle|Process|Manage|Perform|Do|Execute|Run)\s+[A-Z]",
    re.IGNORECASE,
)
_CAMEL_STEP = re.compile(r"^[a-z]+(?:[A-Z][a-z0-9]*)+$")
_PLAIN_ENGLISH = re.compile(r"^[a-z].*(?:\s+[a-z].*)+$", re.IGNORECASE)


class StoryNameCapturesSystemMechanic(PracticeGraphRule):
    slug = "story-name-captures-system-mechanic"
    node_types = ("Story",)

    def check(self, node, context) -> list[str]:
        if _GENERIC_STORY.match(node.name.strip()):
            return [
                f"Story {node.name!r} names a generic handler; use the system mechanic (e.g. 'Submit Order')."
            ]
        return []


class PlainEnglishGwtSteps(PracticeGraphRule):
    slug = "plain-english-gwt-steps"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        text = (node.name or "").strip()
        if not text:
            return []
        if " " not in text and _CAMEL_STEP.match(text):
            return [f"Step {text!r} looks like code; write plain English GWT phrasing."]
        if text.isidentifier() or (text.replace("_", "").isalnum() and " " not in text):
            return [f"Step {text!r} looks like an identifier; write plain English GWT phrasing."]
        if len(text.split()) >= 2 or _PLAIN_ENGLISH.match(text):
            return []
        return []


class RightSizeStoryNodes(PracticeGraphRule):
    """Sibling stories should be distinct intents, not typos or duplicates."""

    slug = "right-size-story-nodes"
    node_types = ("Story",)

    def check_practice(self, context) -> list[tuple[str, str]]:
        by_parent: dict[str, list] = {}
        for story in context.practice.nodes.get("Story", []):
            parent = _story_parent_id(story)
            by_parent.setdefault(parent, []).append(story)
        hits: list[tuple[str, str]] = []
        for stories in by_parent.values():
            if len(stories) < 2:
                continue
            names = [s.name.strip().lower() for s in stories]
            for index, left in enumerate(names):
                for right in names[index + 1 :]:
                    if _is_near_duplicate(left, right):
                        story = stories[names.index(left)]
                        hits.append(
                            (
                                story.node_id,
                                f"Story {story.name!r} is too similar to another story on the same map node.",
                            )
                        )
                        break
        return hits


class VocabularyTracesToDomainSource(PracticeGraphRule):
    slug = "vocabulary-traces-to-domain-source"
    node_types = ("StoryNode", "Epic", "SubEpic", "Story")

    def check(self, node, context) -> list[str]:
        text = node.name or ""
        if re.search(r"\b(payload|dto|request|response|entity|model)\b", text, re.I):
            return [f"{node.type} {text!r} uses technical vocabulary instead of domain language."]
        return []


class ExamplesExportDataNotRepository(PracticeGraphRule):
    slug = "examples-export-data-not-repository"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        relative = node.source.file or ""
        if "repository" in relative.lower() and "examples" in relative.lower():
            return [f"Example file '{relative}' looks like a repository; export data fixtures instead."]
        return []


def _story_parent_id(story) -> str:
    for edge in story.practice.edges.get("belongsTo", []):
        if edge.child is story:
            return edge.parent.node_id
    return ""


def _is_near_duplicate(left: str, right: str) -> bool:
    if left == right:
        return True
    if left.split()[:1] != right.split()[:1]:
        return False
    if abs(len(left) - len(right)) > 2:
        return False
    shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
    return longer.startswith(shorter[: max(3, len(shorter) - 1)])
