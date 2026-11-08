"""BDD rules on spec fixtures — one fault / clean pair per rule."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect, have_len
from mamba import context, description, it

from harness.graph.rule_fixture import SchemaRuleRun

from cdd_guidance.practices.bdd.rules import BY_SLUG
from cdd_guidance.practices.bdd.rules.rule_examples import assert_bdd_source_pair, bdd_rule_by_slug, spec_fixture

_EXAMPLES = _REPO / "cdd_guidance/practices/bdd/model/python/_examples"
_LAYER_FAULT = (_EXAMPLES / "layer-isolation/widget_spec.py").read_text(encoding="utf-8")
_LAYER_CLEAN = "def test_apply():\n    assert True\n"
_OBSERVABLE_FAULT = (_EXAMPLES / "observable-behavior/widget_spec.py").read_text(encoding="utf-8")
_OBSERVABLE_CLEAN = "from expects import equal, expect\n\n\ndef test_greet():\n    expect(widget.names).to(equal(['Ada']))\n"


def _spec(*blocks: str) -> str:
    return "\n".join(blocks) + "\n"


def _failing(source: str, slug: str) -> list[str]:
    """The type of each node the rule reports on in the spec source, run as validate runs it."""
    fixture = spec_fixture(source)
    run = SchemaRuleRun(BY_SLUG[slug], fixture.context)
    return [node.type for node in fixture.context.nodes() if run.node_hits(node)]


with description("BDD example specs"):
    with context("layer-isolation"):
        with it("should flag import-time patch decorators"):
            assert_bdd_source_pair("layer-isolation", _LAYER_FAULT, _LAYER_CLEAN)

    with context("observable-behavior"):
        with it("should flag an assertion on a private member and accept the public one"):
            assert_bdd_source_pair("observable-behavior", _OBSERVABLE_FAULT, _OBSERVABLE_CLEAN)

    with context("describe-is-plain-english"):
        with it("should flag a CamelCase describe and accept a plain-English one"):
            assert_bdd_source_pair(
                "describe-is-plain-english",
                _spec('with description("ShoppingCart totals"):', "    pass"),
                _spec('with description("a shopping cart"):', "    pass"),
            )

    with context("framework-syntax"):
        with it("should flag a spec without a BDD signature marker and accept one that has it"):
            assert_bdd_source_pair(
                "framework-syntax",
                _spec('with description("a cart"):', '    with it("should total zero"):', "        pass"),
                _spec('with description("a cart"):', '    with it("should total zero"):', "        # BDD: SIGNATURE", "        pass"),
            )

    with context("describe-is-subject-not-internal"):
        with it("should flag a describe named after an internal type and accept a domain subject"):
            assert_bdd_source_pair(
                "describe-is-subject-not-internal",
                _spec('with description("the cart manager"):', '    with context("with a Manager"):', "        pass"),
                _spec('with description("a cart"):', '    with context("with one item"):', "        pass"),
            )

    with context("state-not-when"):
        with it("should flag a context that starts with when and accept a that context"):
            assert_bdd_source_pair(
                "state-not-when",
                _spec('with description("a cart"):', '    with context("when emptied"):', "        pass"),
                _spec('with description("a cart"):', '    with context("that was emptied"):', "        pass"),
            )

    with context("one-assertion-per-test"):
        with it("should flag an it with two expects and accept one"):
            assert_bdd_source_pair(
                "one-assertion-per-test",
                _spec(
                    'with description("a cart"):',
                    '    with it("should total zero"):',
                    "        expect(cart.total()).to(equal(0))",
                    "        expect(cart.count()).to(equal(0))",
                ),
                _spec('with description("a cart"):', '    with it("should total zero"):', "        expect(cart.total()).to(equal(0))"),
            )

    with context("no-implementation"):
        with it("should flag a behavior-fidelity it that holds a test body and accept a signature"):
            assert_bdd_source_pair(
                "no-implementation",
                _spec('with description("a cart"):', '    with it("should total zero"):', "        expect(cart.total()).to(equal(0))"),
                _spec('with description("a cart"):', '    with it("should total zero"):', "        # BDD: SIGNATURE", "        pass"),
            )

        with it("should flag a context whose setup runs shared setup, on that context alone"):
            source = _spec(
                'with description("a cart"):',
                '    with context("with one lamp"):',
                "        with before.each:",
                "            self.cart = None",
                '        with it("should total the lamp"):',
                "            # BDD: SIGNATURE",
                "            pass",
            )
            expect(_failing(source, "no-implementation")).to(equal(["Context"]))

        with it("should not repeat an observation's test body on the context around it"):
            source = _spec(
                'with description("a cart"):',
                '    with context("with one lamp"):',
                '        with it("should total the lamp"):',
                "            expect(cart.total()).to(equal(1))",
            )
            expect(_failing(source, "no-implementation")).to(equal(["Observation"]))

    with context("observable-behavior across the describe tree"):
        with it("should report a probe inside an it once"):
            source = _spec('with description("a cart"):', '    with it("should hold the lamp"):', "        expect(subject._lines).to(equal(1))")
            expect(spec_fixture(source).hits(bdd_rule_by_slug("observable-behavior"))).to(have_len(1))

        with it("should report a probe in a context's setup on that context"):
            source = _spec(
                'with description("a cart"):',
                '    with context("with one lamp"):',
                "        lines = subject._lines",
                '        with it("should total the lamp"):',
                "            # BDD: SIGNATURE",
                "            pass",
            )
            expect(_failing(source, "observable-behavior")).to(equal(["Context"]))

    with context("on the node each rule judges"):
        with it("should report a spec that patches infrastructure on the spec"):
            expect(_failing(_LAYER_FAULT, "layer-isolation")).to(equal(["Spec"]))

        with it("should report a context that reads like code on that context"):
            source = _spec('with description("a cart"):', '    with context("with a LineItem"):', "        pass")
            expect(_failing(source, "describe-is-plain-english")).to(equal(["Context"]))

        with it("should report a context named for an internal type on that context"):
            source = _spec('with description("a cart"):', '    with context("with a SessionLog"):', "        pass")
            expect(_failing(source, "describe-is-subject-not-internal")).to(equal(["Context"]))
