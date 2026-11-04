"""Rules that apply to one graph node — same collection shape as practice guidelines."""

from __future__ import annotations

from typing import Any

from harness.guidance.rule import Rule, RulesCollection
from harness.graph.practice_rule import PracticeGraphRule


class GraphRule(PracticeGraphRule, Rule):
    """One schema rule on a node: slug, prose body, and optional executable check."""

    def __init__(
        self,
        slug: str,
        body: str = "",
        node_types: tuple[str, ...] = (),
        *,
        executable: bool = False,
    ) -> None:
        PracticeGraphRule.__init__(self)
        Rule.__init__(self, slug=slug, body=body)
        self.slug = slug
        self.node_types = node_types
        self.executable = executable
        self._violations: list[str] = []
        self.hits: list[dict] = []

    @classmethod
    def from_check(cls, check: PracticeGraphRule, body: str = "") -> GraphRule:
        rule = cls(
            check.slug,
            body=body,
            node_types=tuple(check.node_types),
            executable=True,
        )
        rule.check = check.check  # type: ignore[method-assign]
        return rule

    @classmethod
    def prose_only(cls, slug: str, body: str = "", node_types: tuple[str, ...] = ()) -> GraphRule:
        return cls(slug, body=body, node_types=node_types, executable=False)

    @classmethod
    def prompt_only(cls, slug: str, node_types: tuple[str, ...] = ()) -> GraphRule:
        """Alias for prose-only rules with no markdown body loaded yet."""
        return cls.prose_only(slug, body="", node_types=node_types)

    @property
    def violations(self) -> list[str]:
        return list(self._violations)

    def record(self, message: str, source: Any = None) -> None:
        """Keep message as a violation of this rule at source, the node's place in its file; a hit with no source has
        no file or lines."""
        text = (message or "").strip()
        if text and text not in self._violations:
            self._violations.append(text)
            self.hits.append({
                "message": text,
                "file": getattr(source, "file", "") or "",
                "start": int(getattr(source, "start_line", 0) or 0),
                "end": int(getattr(source, "end_line", 0) or 0),
            })

    def clear_violations(self) -> None:
        self._violations.clear()
        self.hits.clear()

    @property
    def is_failing(self) -> bool:
        return bool(self._violations)


class GraphRulesCollection(RulesCollection):
    """Schema rules for one node. Violations live on each GraphRule entry."""

    def __init__(self, node: Any, entries: dict[str, GraphRule] | None = None) -> None:
        super().__init__(entries)
        self.node = node

    @property
    def slugs(self) -> list[str]:
        return list(self.entries.keys())

    @property
    def violations(self) -> list[tuple[str, str]]:
        """Each violation on this node as its rule's slug and its message."""
        return [(rule.slug, message) for rule in self.graph_rules for message in rule.violations]

    @property
    def failed_slugs(self) -> list[str]:
        return list(dict.fromkeys(slug for slug, _message in self.violations))

    @property
    def passing_slugs(self) -> list[str]:
        failed = set(self.failed_slugs)
        return [slug for slug in self.slugs if slug not in failed]

    @property
    def graph_rules(self) -> list[GraphRule]:
        return [value for value in self.entries.values() if isinstance(value, GraphRule)]

    def record_violation(self, slug: str, message: str) -> None:
        """Keep message as a violation of the rule slug, at this node's source. A slug this node has no rule for
        records nothing, since the rule does not apply to it."""
        entry = self.entries.get(slug)
        if isinstance(entry, GraphRule):
            entry.record(message, getattr(self.node, "source", None))

    def clear_violations(self) -> None:
        for rule in self.graph_rules:
            rule.clear_violations()
