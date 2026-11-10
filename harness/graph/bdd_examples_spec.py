"""BDD rules on spec fixtures — one fault / clean pair per rule."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mamba import context, description, it

from harness.graph.bdd_example_harness import assert_bdd_source_pair

_EXAMPLES = _REPO / "cdd_guidance/practices/bdd/model/python/_examples"
_LAYER_FAULT = (_EXAMPLES / "layer-isolation/widget_spec.py").read_text(encoding="utf-8")
_LAYER_CLEAN = "def test_apply():\n    assert True\n"
_OBSERVABLE_FAULT = (_EXAMPLES / "observable-behavior/widget_spec.py").read_text(encoding="utf-8")
_OBSERVABLE_CLEAN = "from expects import equal, expect\n\n\ndef test_greet():\n    expect(widget.names).to(equal(['Ada']))\n"


def _spec(*blocks: str) -> str:
    return "\n".join(blocks) + "\n"


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
                _spec('with description("a cart"):', '    with it("should total zero"):', "        # BDD: SIGNATURE"),
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
                _spec('with description("a cart"):', '    with it("should total zero"):', "        # BDD: SIGNATURE"),
            )
