"""UX graph rule classes — add checks ported from historical scanners on main."""

from harness.graph.practice_rule import PracticeGraphRule

RULES: tuple[PracticeGraphRule, ...] = ()
BY_SLUG: dict[str, PracticeGraphRule] = {}

__all__ = ["BY_SLUG", "RULES"]
