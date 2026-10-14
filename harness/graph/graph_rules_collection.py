"""Rules that apply to one graph node — same collection shape as practice guidelines."""

from __future__ import annotations

from typing import Any, Iterator

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

    def record(self, message: str, file: str = "", start: int = 0, end: int = 0) -> None:
        text = (message or "").strip()
        if text and text not in self._violations:
            self._violations.append(text)
            self.hits.append(
                {"message": text, "file": file, "start": int(start or 0), "end": int(end or 0)}
            )

    def clear_violations(self) -> None:
        self._violations.clear()
        self.hits.clear()

    def failing(self) -> bool:
        return bool(self._violations)


class GraphRulesCollection(RulesCollection):
    """Schema rules for one node. Violations live on each GraphRule entry."""

    def __init__(
        self,
        node: Any,
        entries: dict[str, GraphRule] | None = None,
        parent: Any = None,
    ) -> None:
        super().__init__(entries, parent=parent)
        self.node = node

    def slugs(self) -> list[str]:
        return list(self.entries.keys())

    def violations(self) -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for rule in self.graph_rules():
            for message in rule.violations:
                hits.append((rule.slug, message))
        return hits

    def failed_slugs(self) -> list[str]:
        found: list[str] = []
        for slug, _message in self.violations():
            if slug not in found:
                found.append(slug)
        return found

    def passing_slugs(self) -> list[str]:
        failed = set(self.failed_slugs())
        return [slug for slug in self.slugs() if slug not in failed]

    def graph_rules(self) -> Iterator[GraphRule]:
        for value in self.entries.values():
            if isinstance(value, GraphRule):
                yield value

    def record_violation(
        self,
        slug: str,
        message: str,
        file: str | None = None,
        start: int | None = None,
        end: int | None = None,
    ) -> None:
        entry = self.entries.get(slug)
        if not isinstance(entry, GraphRule):
            return
        source = getattr(self.node, "source", None)
        if file is None and source is not None:
            file = source.file
            start = source.start_line
            end = source.end_line
        entry.record(message, file or "", int(start or 0), int(end or 0))

    def clear_violations(self) -> None:
        for rule in self.graph_rules():
            rule.clear_violations()
