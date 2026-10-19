"""TypeScript story-artifact rules — add file-channel checks ported from historical scanners."""

from harness.graph.practice_rule import PracticeGraphRule

RULES: tuple[PracticeGraphRule, ...] = ()
BY_SLUG: dict[str, PracticeGraphRule] = {}

__all__ = ["BY_SLUG", "RULES"]
