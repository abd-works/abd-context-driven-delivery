"""UX rules from practices/ux/scanners (main history) — graph Screen / UxMap nodes."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class ScreenStoryBudget(PracticeGraphRule):
    slug = "screen-story-budget"
    node_types = ("Screen",)
    soft_max = 4

    def check(self, node, context) -> list[str]:
        count = context.child_count(node, ("stories",))
        if count <= self.soft_max:
            return []
        return [
            f"Screen {node.name!r} has {count} stories (budget ~{self.soft_max})."
        ]


class ScreenNamesUseDomainTerms(PracticeGraphRule):
    slug = "screen-names-use-domain-terms"
    node_types = ("Screen",)

    def check(self, node, context) -> list[str]:
        name = node.name.strip()
        if not name:
            return ["Screen name is empty."]
        if name.lower() in {"screen", "page", "view", "home", "main"}:
            return [f"Screen {name!r} should use a domain term, not a generic label."]
        return []
