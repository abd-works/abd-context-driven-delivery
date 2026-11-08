"""Spec support: BDD rule checks on spec fixtures, loaded through the real working-copy build.

The spec file's language model parses its describe tree and every node loads its own facts;
rules read only those facts.
"""

from __future__ import annotations

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.bdd.rules import BY_SLUG


def bdd_rule_by_slug(slug: str):
    return BY_SLUG[slug]


def spec_fixture(source: str, *, filename: str = "widget_spec.py") -> RuleFixture:
    """The spec source, read by BDD from a folder of its own."""
    return RuleFixture(Bdd, {filename: source.strip() + "\n"})


def assert_bdd_source_pair(slug: str, fault: str, clean: str, *, filename: str = "widget_spec.py") -> None:
    RulePair(bdd_rule_by_slug(slug), spec_fixture(fault, filename=filename), spec_fixture(clean, filename=filename)).check()
