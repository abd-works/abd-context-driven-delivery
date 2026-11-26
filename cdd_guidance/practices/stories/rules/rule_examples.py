"""Spec support: run Stories graph rules on example story tests the way validate runs them.

An example is a folder of story tests in the layout a build reads (`tests/<epic>/<sub-epic>_story.test.ts`). The
folder is read through the real working-copy build, so Stories' own TypeScript format reads each story test into the
story map and every node carries the type and facts a live build gives it. Each rule then runs through the practice's
schema, so a rule the schema never applies to a node type finds nothing there and its example fails. An example that
holds a domain model document (`domain-model.md`) is read with DDD beside Stories, so a rule that applies only where a
model is written, such as then-observes-an-example, has the model its example links to.
"""

from __future__ import annotations

from functools import partial
from pathlib import Path

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.rules import BY_SLUG
from cdd_guidance.practices.stories.stories import Stories

_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "typescript" / "_examples"
_DOMAIN_MODEL_FILE = "domain-model.md"


def stories_fixture(folder: Path) -> RuleFixture:
    """The files under folder, named from it, read by Stories as a live load reads a working copy."""
    files = {path.relative_to(folder).as_posix(): path.read_text(encoding="utf-8") for path in folder.rglob("*") if path.is_file()}
    models = (Ddd,) if any(Path(file).name == _DOMAIN_MODEL_FILE for file in files) else ()
    return RuleFixture(Stories, files, beside=models)


def assert_stories_example_pair(slug: str) -> None:
    """The rule flags the story tests of its example's faulty folder and passes those of its repaired one."""
    root = _EXAMPLES / slug
    RulePair(BY_SLUG[slug], stories_fixture(root / "faulty"), stories_fixture(root / "repaired")).check()


def _has_both_sides(slug: str) -> bool:
    return (_EXAMPLES / slug / "faulty").is_dir() and (_EXAMPLES / slug / "repaired").is_dir()


def _map(*sub_epics: tuple[str, int]) -> str:
    """A story map of the epic Sell Books, holding each sub-epic with that many stories."""
    lines = ["# (E) Sell Books"]
    for name, stories in sub_epics:
        lines.append(f"## (E) {name}")
        lines += [f"### (S) Customer --> {name} Step {order}" for order in range(1, stories + 1)]
    return "\n".join(lines) + "\n"


_TAKE_ORDERS_MAP = "# (E) Sell Books\n## (E) Take Orders\n### (S) Customer --> Place Order\n### (S) Customer --> Cancel Order\n"
_SCENARIOS_FILE = "story_tests/sell-books/take-orders/take_orders_story.test.md"


def _scenarios(story: str, *scenarios: str) -> dict[str, str]:
    """The Take Orders map with a scenarios file that heads the given scenarios with story."""
    return {"story-map.md": _TAKE_ORDERS_MAP, _SCENARIOS_FILE: f"# Sub-epic: Take Orders\n\n## Story: {story}\n\n" + "\n".join(scenarios)}


def _scenario(name: str, when: str = "the Customer places an order for one book") -> str:
    return f"#### Scenario: {name}\n\n*Given* a Customer with an empty basket\n*When* {when}\n*Then* the order holds one line\n"


def _outline(rows: int) -> str:
    table = "\n".join(f"| order {row} | {row} |" for row in range(1, rows + 1))
    return (
        "#### Scenario Outline: Order books\n\n*Given* a Customer with an empty basket\n*When* the Customer orders {copies} books\n"
        f"*Then* the order holds {{copies}} lines\n\n#### Examples\n\n| scenario | copies |\n|----------|--------|\n{table}\n"
    )


_STORY_TEST_FILE = "story_tests/sell-books/take-orders/place_order_story.test.py"
# Clean Engineering read beside Stories, as every live graph reads it, so a step's calls are linked to code.
_CODE_READ = (CleanEngineering,)


def _story_test(given: str, when: str, then: str) -> dict[str, str]:
    """The Take Orders map with a Python story test of Place Order whose steps run the given lines."""
    test = (
        "from story_test import given, scenario, story, then, when\n\n# Epic: Sell Books\n# Sub-epic: Take Orders\n\n"
        '# Story: Place Order\n# Actor: Customer\nwith story("Place Order"):\n    with scenario("Order one book"):\n'
        f'        with given("a Customer with an empty basket"):\n            {given}\n'
        f'        with when("the Customer places an order for one book"):\n            {when}\n'
        f'        with then("the order holds one line"):\n            {then}\n'
    )
    return {"story-map.md": _TAKE_ORDERS_MAP, _STORY_TEST_FILE: test}


def _steps_scenario(name: str, *steps: str) -> str:
    """A scenario of the given step lines, each already written with its keyword: ``*Given* a Customer``."""
    return f"#### Scenario: {name}\n\n" + "\n".join(steps) + "\n"


def _realized(when: str, call: str) -> str:
    """A When line with the realization block that names the first operation it calls."""
    return f"*When* {when}\n\n```realization\n{call}\n  <- Book[] the catalog shows\n```\n"


# A Given whose whole predicate is an example's name, and the same Given saying in domain words what the basket holds.
_EXAMPLE_NAME_GIVEN = "*Given* the ++[basket](domain-model.md#basket)++ is ++Me on the checklist++"
_DOMAIN_WORDS_GIVEN = "*Given* the ++[basket](domain-model.md#basket)++ holds ++one book set aside for Me++"
_ORDER_STEPS = ("*When* the **Customer** places an order for one book", "*Then* the order holds one line")
# Two scenarios that run the same operation and check mostly the same outcome; repaired, the second shows another case.
_SEE_CATALOG = _steps_scenario("See the catalog", "*Given* the **Customer** has an ++empty basket++",
    _realized("the **Customer** opens the shop", "BookRepository.list()"),
    "*Then* the catalog shows ++Dune++ and ++Emma++, each with its price", "  *And* ++Dune++ is tagged *Best value*")
_LOAD_CATALOG = _steps_scenario("Load catalog", "*Given* the **Customer** has an ++empty basket++",
    _realized("the catalog is loaded", "BookRepository.list()"),
    "*Then* the catalog shows ++Dune++ and ++Emma++", "  *And* ++Dune++ is tagged *Best value*", "  *But* ++Secret++ is not in the catalog")
_EMPTY_CATALOG = _steps_scenario("See an empty catalog", "*Given* the shop sells no book",
    _realized("the **Customer** opens the shop", "BookRepository.list()"), "*Then* the catalog says no book is for sale")
# A scenario of the Customer's story in which only the system looks something up; repaired, the Customer acts.
_LOOKUP_ONLY = _steps_scenario("No profile before the account is verified", "*Given* the **Customer** has an unverified account",
    "*When* My Shop looks for the customer profile of the account", "*Then* no profile is found")
_CUSTOMER_ACTS = _steps_scenario("No profile before the account is verified", "*Given* the **Customer** has an unverified account",
    "*When* the **Customer** opens the profile page", "*Then* the page says the account is not verified yet")


# A rule's failing files and its repaired files, written here where an example folder of story tests would say no more:
# each side is a small story map, with a scenarios file or a story test where the rule reads one.
FILE_PAIRS: dict[str, tuple[dict[str, str], dict[str, str]]] = {
    "child-count-fits-layer": (
        {"story-map.md": _map(("Take Orders", 2))},
        {"story-map.md": _map(("Take Orders", 2), ("Ship Orders", 2))},
    ),
    "outline-requires-many-permutations": (_scenarios("Place Order", _outline(2)), _scenarios("Place Order", _outline(3))),
    "scenarios-name-a-story-on-the-map": (_scenarios("Refund Order", _scenario("Order one book")), _scenarios("Place Order", _scenario("Order one book"))),
    "when-holds-the-operation": (_scenarios("Place Order", _scenario("Order one book", when="…")), _scenarios("Place Order", _scenario("Order one book"))),
    "story-scenarios-at-most-seven": (
        _scenarios("Place Order", *(_scenario(f"Order book {number}") for number in range(1, 9))),
        _scenarios("Place Order", *(_scenario(f"Order book {number}") for number in range(1, 3))),
    ),
    "step-says-more-than-an-example-name": (
        _scenarios("Place Order", _steps_scenario("Order from the checklist", _EXAMPLE_NAME_GIVEN, *_ORDER_STEPS)),
        _scenarios("Place Order", _steps_scenario("Order from the checklist", _DOMAIN_WORDS_GIVEN, *_ORDER_STEPS)),
    ),
    "scenarios-differ-in-when-or-outcome": (
        _scenarios("Place Order", _SEE_CATALOG, _LOAD_CATALOG),
        _scenarios("Place Order", _SEE_CATALOG, _EMPTY_CATALOG),
    ),
    "person-stories-show-the-person-acting": (_scenarios("Place Order", _LOOKUP_ONLY), _scenarios("Place Order", _CUSTOMER_ACTS)),
    # A story at acceptance tests, since its Given has a body, whose When calls nothing; repaired, the When calls the
    # operation it tests.
    "code-steps-invoke-code": (
        _story_test("basket = Basket()", "pass", "expect(order.lines).to(have_len(1))"),
        _story_test("basket = Basket()", "order = basket.place()", "expect(order.lines).to(have_len(1))"),
    ),
}


def assert_stories_files_pair(slug: str) -> None:
    """The rule flags the files of its failing side and passes those of its repaired side (``FILE_PAIRS``)."""
    faulty, repaired = FILE_PAIRS[slug]
    RulePair(BY_SLUG[slug], RuleFixture(Stories, faulty, beside=_CODE_READ), RuleFixture(Stories, repaired, beside=_CODE_READ)).check()


# What proves each rule flags its failing example and passes its repaired one, for the spec every practice shares: a
# rule has a pair once its example folder holds a faulty and a repaired side, or it is written above.
EXAMPLE_PAIRS = {
    **{slug: partial(assert_stories_example_pair, slug) for slug in BY_SLUG if _has_both_sides(slug)},
    **{slug: partial(assert_stories_files_pair, slug) for slug in FILE_PAIRS},
}
