"""DDD graph rule classes (schema slugs; checks added per rule)."""

from harness.graph.practice_rule import PracticeGraphRule

RULES: tuple[PracticeGraphRule, ...] = ()
BY_SLUG: dict[str, PracticeGraphRule] = {}

__all__ = ["BY_SLUG", "RULES"]
