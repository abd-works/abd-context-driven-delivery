"""Load graph rules per practice and per model language channel."""

from __future__ import annotations

import importlib
from functools import lru_cache

from harness.graph.language_for_node import language_for_node
from harness.graph.practice_rule import PracticeGraphRule

_PRACTICE_GRAPH_RULES = {
    "clean_engineering": "practices.clean_engineering.rules",
    "stories": "practices.stories.rules",
    "ddd": "practices.ddd.rules",
    "bdd": "practices.bdd.rules",
    "ux": "practices.ux.rules",
}

_CE_LANGUAGE_RULES = {
    "python": "practices.clean_engineering.model.python.rules",
    "typescript": "practices.clean_engineering.model.typescript.rules",
    "javascript": "practices.clean_engineering.model.javascript.rules",
    "drawio": "practices.clean_engineering.model.drawio.rules",
}

_STORIES_LANGUAGE_RULES = {
    "typescript": "practices.stories.model.typescript.rules",
    "javascript": "practices.stories.model.javascript.rules",
}


def _load_module_rules(module_path: str) -> dict[str, PracticeGraphRule]:
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return {}
    by_slug = getattr(module, "BY_SLUG", None)
    if isinstance(by_slug, dict):
        return dict(by_slug)
    rules = getattr(module, "RULES", ())
    return {rule.slug: rule for rule in rules if getattr(rule, "slug", "")}


@lru_cache(maxsize=None)
def graph_rules_for_practice(practice: str) -> dict[str, PracticeGraphRule]:
    path = _PRACTICE_GRAPH_RULES.get(practice)
    if path is None:
        return {}
    return _load_module_rules(path)


@lru_cache(maxsize=None)
def language_rules_for_practice(practice: str, language: str) -> dict[str, PracticeGraphRule]:
    if practice == "clean_engineering":
        path = _CE_LANGUAGE_RULES.get(language)
    elif practice == "stories":
        path = _STORIES_LANGUAGE_RULES.get(language)
    else:
        path = None
    if path is None:
        return {}
    return _load_module_rules(path)


def checks_for_practice(practice: str) -> dict[str, PracticeGraphRule]:
    """All registered checks (graph + every language channel) for listing."""
    merged = dict(graph_rules_for_practice(practice))
    if practice == "clean_engineering":
        for language in _CE_LANGUAGE_RULES:
            for slug, rule in language_rules_for_practice(practice, language).items():
                merged.setdefault(slug, rule)
    elif practice == "stories":
        for language in _STORIES_LANGUAGE_RULES:
            for slug, rule in language_rules_for_practice(practice, language).items():
                merged.setdefault(slug, rule)
    return merged


def checks_for_node(node) -> dict[str, PracticeGraphRule]:
    """Checks that apply to this node type and source language."""
    practice_name = node.practice.name
    language = language_for_node(node)
    merged = dict(graph_rules_for_practice(practice_name))
    if language and language != "graph":
        merged.update(language_rules_for_practice(practice_name, language))
    applicable: dict[str, PracticeGraphRule] = {}
    for slug, rule in merged.items():
        if rule.applies_to(node.type):
            applicable[slug] = rule
    return applicable
