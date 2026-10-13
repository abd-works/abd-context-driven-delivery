"""Load each practice's rules/ package."""

from __future__ import annotations

import importlib
from functools import lru_cache

from harness.graph.practice_rule import PracticeGraphRule

_PRACTICE_MODULES = {
    "clean_engineering": "practices.clean_engineering.rules",
    "stories": "practices.stories.rules",
    "ddd": "practices.ddd.rules",
    "bdd": "practices.bdd.rules",
    "ux": "practices.ux.rules",
}


@lru_cache(maxsize=None)
def checks_for_practice(practice: str) -> dict[str, PracticeGraphRule]:
    module_path = _PRACTICE_MODULES.get(practice)
    if module_path is None:
        return {}
    module = importlib.import_module(module_path)
    by_slug = getattr(module, "BY_SLUG", None)
    if isinstance(by_slug, dict):
        return dict(by_slug)
    rules = getattr(module, "RULES", ())
    return {rule.slug: rule for rule in rules if rule.slug}


def all_checks() -> dict[str, PracticeGraphRule]:
    merged: dict[str, PracticeGraphRule] = {}
    for practice in _PRACTICE_MODULES:
        for slug, rule in checks_for_practice(practice).items():
            merged.setdefault(slug, rule)
    return merged
