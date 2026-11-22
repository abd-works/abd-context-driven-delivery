"""Spec support: TDD's coverage rules on small projects of code and the specs that test it, read through the real
working-copy build with TDD's overlay, as a live load reads them. Each rule's failing example and its repaired one are
kept here, by the rule's slug."""

from __future__ import annotations

from functools import partial

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.tdd.rules import BY_SLUG


def tested_code_fixture(files: dict[str, str]) -> RuleFixture:
    """Code read by Clean Engineering with the specs beside it read by BDD, so each observation is linked to the
    operations it invokes."""
    return RuleFixture(CleanEngineering, {name: text.strip() + "\n" for name, text in files.items()}, beside=(Bdd,))


def specs_fixture(files: dict[str, str]) -> RuleFixture:
    """Spec files read by BDD, each at the tier its name puts it in."""
    return RuleFixture(Bdd, {name: text.strip() + "\n" for name, text in files.items()})


def assert_tdd_example_pair(slug: str) -> None:
    """The rule flags its failing example and passes its repaired one (``EXAMPLES``)."""
    make, fault, clean = EXAMPLES[slug]
    RulePair(BY_SLUG[slug], make(fault), make(clean)).check()


_CART = '''
class CartAlreadyCheckedOut(Exception):
    """The cart was checked out before."""


class Cart:
    def __init__(self):
        self.items = []
        self.is_checked_out = False

    def add(self, item):
        self.items.append(item)

    def check_out(self):
        if self.is_checked_out:
            raise CartAlreadyCheckedOut(self)
        self.is_checked_out = True
'''

_SPEC_OF_ADD = '''
from expects import equal, expect, raise_error
from mamba import description, it

from cart import Cart

with description("a cart"):
    with it("should hold an item added to it"):
        cart = Cart()
        cart.add("book")
        expect(cart.items).to(equal(["book"]))
'''

_SPEC_OF_ADD_AND_CHECK_OUT = _SPEC_OF_ADD.rstrip() + '''

    with it("should be checked out"):
        cart = Cart()
        cart.check_out()
        expect(cart.is_checked_out).to(equal(True))
'''

_SPEC_OF_SECOND_CHECK_OUT = _SPEC_OF_ADD_AND_CHECK_OUT.rstrip() + '''

    with it("should refuse a second check out"):
        from cart import CartAlreadyCheckedOut
        cart = Cart()
        cart.check_out()
        expect(cart.check_out).to(raise_error(CartAlreadyCheckedOut))
'''

SPEC_REACHING_A_PROCESS = '''
import subprocess
from mamba import description, it

with description("a widget"):
    with it("should start"):
        subprocess.run(["widget"])
'''

_SPEC_WITH_NO_REAL_RESOURCE = '''
from mamba import description, it

with description("a widget"):
    with it("should start"):
        launcher.run(["widget"])
'''

_UNIT_SPEC_WITH_A_STUB = '''
from unittest import mock
from mamba import description, it

with description("a repository"):
    with it("should push its branch"):
        with mock.patch("repo.run_git") as run_git:
            Repo().push()
'''

_HEAVY_SPEC_OF_ANOTHER_SENTENCE = '''
from mamba import description, it

with description("a repository"):
    with it("should list its branches"):
        Repo().branches()
'''

_HEAVY_SPEC_OF_THE_SAME_SENTENCE = '''
from mamba import description, it

with description("a repository"):
    with it("should push its branch"):
        Repo().push()
'''

# Each coverage rule's fixture maker, failing files and repaired files, by the rule's slug.
EXAMPLES: dict[str, tuple] = {
    "unit-tier-fakes-every-boundary": (
        specs_fixture,
        {"widget_spec.py": SPEC_REACHING_A_PROCESS},
        {"widget_spec.py": _SPEC_WITH_NO_REAL_RESOURCE},
    ),
    "operation-has-a-proving-test": (
        tested_code_fixture,
        {"cart.py": _CART, "cart_spec.py": _SPEC_OF_ADD},
        {"cart.py": _CART, "cart_spec.py": _SPEC_OF_SECOND_CHECK_OUT},
    ),
    "declared-exception-raised-by-a-test": (
        tested_code_fixture,
        {"cart.py": _CART, "cart_spec.py": _SPEC_OF_ADD_AND_CHECK_OUT},
        {"cart.py": _CART, "cart_spec.py": _SPEC_OF_SECOND_CHECK_OUT},
    ),
    "stubbed-boundary-has-heavy-coverage": (
        specs_fixture,
        {"repo_spec.py": _UNIT_SPEC_WITH_A_STUB, "repo_heavy_spec.py": _HEAVY_SPEC_OF_ANOTHER_SENTENCE},
        {"repo_spec.py": _UNIT_SPEC_WITH_A_STUB, "repo_heavy_spec.py": _HEAVY_SPEC_OF_THE_SAME_SENTENCE},
    ),
}

# What proves each rule flags its failing example and passes its repaired one, for the spec every practice shares.
EXAMPLE_PAIRS = {slug: partial(assert_tdd_example_pair, slug) for slug in EXAMPLES}
