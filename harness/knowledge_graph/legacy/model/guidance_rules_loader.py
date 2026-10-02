"""Wrap the Rule objects already owned by each practice."""

from __future__ import annotations

import sys
from typing import List

from harness.guidance.rule import Rule

from .graph_rules import GraphRule


def load_graph_rules_from_markdown(root=None) -> List[GraphRule]:
    from practices.bdd.bdd import Bdd
    from practices.clean_engineering.clean_engineering import CleanEngineering
    from practices.clean_engineering.specifications.lern_domain_driven.lern_domain_driven import (
        LernDomainDriven,
    )
    from practices.ddd.ddd import Ddd
    from practices.stories.stories import Stories
    from practices.ux.ux import Ux

    wrapped: List[GraphRule] = []
    for practice, factory in (
        ("stories", Stories),
        ("clean_engineering", CleanEngineering),
        ("ddd", Ddd),
        ("bdd", Bdd),
        ("ux", Ux),
        ("lern_domain_driven", LernDomainDriven),
    ):
        try:
            guidance = factory()
        except Exception as error:
            print(f"skipped {practice} rules ({error})", file=sys.stderr)
            continue
        wrapped.extend(_wrap(guidance.rules, practice=practice, shared=True))
        fidelities = getattr(guidance, "fidelities", None)
        if fidelities is not None:
            for name, child in getattr(fidelities, "entries", {}).items():
                child_rules = getattr(child, "rules", None)
                for rule in _wrap(child_rules, practice=practice, shared=False):
                    if rule.fidelity is None:
                        rule.fidelity = getattr(child, "fidelity", None) or name
                    wrapped.append(rule)
        wrapped.extend(guidance.project_rules(root))
    return wrapped


def _wrap(collection, *, practice: str, shared: bool) -> List[GraphRule]:
    if collection is None:
        return []
    wrapped: List[GraphRule] = []
    for rule in collection:
        if isinstance(rule, GraphRule):
            wrapped.append(rule)
        elif isinstance(rule, Rule):
            wrapped.append(GraphRule(rule, practice=practice, shared=shared, tag="base"))
    return wrapped
