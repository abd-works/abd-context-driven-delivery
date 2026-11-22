"""Spec support: BDD rule checks on spec fixtures, loaded through the real working-copy build.

The spec file's language model parses its describe tree and every node loads its own facts;
rules read only those facts.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.bdd.rules import BY_SLUG


def spec_fixture(source: str, *, filename: str = "widget_spec.py") -> RuleFixture:
    """The spec source, read by BDD from a folder of its own."""
    return RuleFixture(Bdd, {filename: source.strip() + "\n"})


def assert_bdd_source_pair(slug: str, fault: str, clean: str, *, filename: str = "widget_spec.py") -> None:
    RulePair(BY_SLUG[slug], spec_fixture(fault, filename=filename), spec_fixture(clean, filename=filename)).check()


def assert_bdd_example_pair(slug: str) -> None:
    """The rule flags its failing example and passes its repaired one (``EXAMPLE_SOURCES``)."""
    fault, clean = EXAMPLE_SOURCES[slug]
    assert_bdd_source_pair(slug, fault, clean)


def _spec(*blocks: str) -> str:
    return "\n".join(blocks) + "\n"


_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "python" / "_examples"
_LAYER_FAULT = (_EXAMPLES / "layer-isolation/widget_spec.py").read_text(encoding="utf-8")
_LAYER_CLEAN = "def test_apply():\n    assert True\n"
_OBSERVABLE_FAULT = (_EXAMPLES / "observable-behavior/widget_spec.py").read_text(encoding="utf-8")
_OBSERVABLE_CLEAN = "from expects import equal, expect\n\n\ndef test_greet():\n    expect(widget.names).to(equal(['Ada']))\n"
_FAULT = """
with description("a bare agentic toolset registered for deploy"):
    pass

with description("a bare agentic toolset with mcp-published operations registered for deploy"):
    pass
"""

_CLEAN = """
with description("a bare agentic toolset registered for deploy"):
    with context("with no mcp-published operations"):
        pass
    with context("with mcp-published operations"):
        pass
"""

# Each checked rule's failing spec and its repaired one, by the rule's slug: the one place a rule's example pair is kept.
EXAMPLE_SOURCES: dict[str, tuple[str, str]] = {
    "layer-isolation": (
        _LAYER_FAULT,
        _LAYER_CLEAN,
    ),
    "observable-behavior": (
        _OBSERVABLE_FAULT,
        _OBSERVABLE_CLEAN,
    ),
    "describe-is-plain-english": (
        _spec('with description("ShoppingCart totals"):', "    pass"),
        _spec('with description("a shopping cart"):', "    pass"),
    ),
    "framework-syntax": (
        _spec('with description("a cart"):', '    with it("should total zero"):', "        pass"),
        _spec('with description("a cart"):', '    with it("should total zero"):', "        # BDD: SIGNATURE", "        pass"),
    ),
    "describe-is-subject-not-internal": (
        _spec('with description("the cart manager"):', '    with context("with a Manager"):', "        pass"),
        _spec('with description("a cart"):', '    with context("with one item"):', "        pass"),
    ),
    "state-not-when": (
        _spec('with description("a cart"):', '    with context("when emptied"):', "        pass"),
        _spec('with description("a cart"):', '    with context("that was emptied"):', "        pass"),
    ),
    "one-assertion-per-test": (
        _spec(
                    'with description("a cart"):',
                    '    with it("should total zero"):',
                    "        expect(cart.total()).to(equal(0))",
                    "        expect(cart.count()).to(equal(0))",
                ),
        _spec('with description("a cart"):', '    with it("should total zero"):', "        expect(cart.total()).to(equal(0))"),
    ),
    "no-implementation": (
        _spec(
                    'with description("a cart"):',
                    '    with it("should total zero"):',
                    "        expect(cart.total()).to(equal(0))",
                    '    with it("should count zero"):',
                    "        # BDD: SIGNATURE",
                    "        pass",
                ),
        _spec('with description("a cart"):', '    with it("should total zero"):', "        # BDD: SIGNATURE", "        pass"),
    ),
    "shared-describe-subject": (_FAULT, _CLEAN),
}
# What proves each rule flags its failing example and passes its repaired one, for the spec every practice shares.
EXAMPLE_PAIRS = {slug: partial(assert_bdd_example_pair, slug) for slug in EXAMPLE_SOURCES}
