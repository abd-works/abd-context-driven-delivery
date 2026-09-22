"""Wrap the Rule objects already owned by each practice."""

from __future__ import annotations

from typing import List

from actions.scan.rule import Rule

from .graph_rules import GraphRule


def load_graph_rules_from_markdown() -> List[GraphRule]:
    from practices.bdd.bdd import Bdd
    from practices.clean_engineering.clean_engineering import CleanEngineering
    from practices.ddd.ddd import Ddd
    from practices.stories.stories import Stories

    wrapped: List[GraphRule] = []
    for practice, guidance in (
        ("stories", Stories()),
        ("clean_engineering", CleanEngineering()),
        ("ddd", Ddd()),
        ("bdd", Bdd()),
    ):
        wrapped.extend(_wrap(guidance.rules, practice=practice, shared=True))
        fidelities = getattr(guidance, "fidelities", None)
        if fidelities is None:
            continue
        for name, child in getattr(fidelities, "entries", {}).items():
            child_rules = getattr(child, "rules", None)
            for rule in _wrap(child_rules, practice=practice, shared=False):
                if rule.fidelity is None:
                    rule.rule.fidelity = getattr(child, "fidelity", None) or name
                wrapped.append(rule)
    return wrapped


def _wrap(collection, *, practice: str, shared: bool) -> List[GraphRule]:
    if collection is None:
        return []
    return [
        GraphRule(rule, practice=practice, shared=shared)
        for rule in collection
        if isinstance(rule, Rule)
    ]
