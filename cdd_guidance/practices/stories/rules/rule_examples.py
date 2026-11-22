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


# A rule's failing files and its repaired files, written here where an example folder of story tests would say no more:
# each side is a small story map, with a scenarios file where the rule reads one.
MARKDOWN_PAIRS: dict[str, tuple[dict[str, str], dict[str, str]]] = {
    "child-count-fits-layer": (
        {"story-map.md": _map(("Take Orders", 2), ("Ship Orders", 2))},
        {"story-map.md": _map(("Take Orders", 2), ("Ship Orders", 2), ("Refund Orders", 2))},
    ),
    "outline-requires-many-permutations": (_scenarios("Place Order", _outline(2)), _scenarios("Place Order", _outline(3))),
    "scenarios-name-a-story-on-the-map": (_scenarios("Refund Order", _scenario("Order one book")), _scenarios("Place Order", _scenario("Order one book"))),
    "when-holds-the-operation": (_scenarios("Place Order", _scenario("Order one book", when="…")), _scenarios("Place Order", _scenario("Order one book"))),
    "story-scenarios-at-most-seven": (
        _scenarios("Place Order", *(_scenario(f"Order book {number}") for number in range(1, 9))),
        _scenarios("Place Order", *(_scenario(f"Order book {number}") for number in range(1, 3))),
    ),
}


def assert_stories_markdown_pair(slug: str) -> None:
    """The rule flags the files of its failing side and passes those of its repaired side (``MARKDOWN_PAIRS``)."""
    faulty, repaired = MARKDOWN_PAIRS[slug]
    RulePair(BY_SLUG[slug], RuleFixture(Stories, faulty), RuleFixture(Stories, repaired)).check()


# What proves each rule flags its failing example and passes its repaired one, for the spec every practice shares: a
# rule has a pair once its example folder holds a faulty and a repaired side, or it is written above.
EXAMPLE_PAIRS = {
    **{slug: partial(assert_stories_example_pair, slug) for slug in BY_SLUG if _has_both_sides(slug)},
    **{slug: partial(assert_stories_markdown_pair, slug) for slug in MARKDOWN_PAIRS},
}
