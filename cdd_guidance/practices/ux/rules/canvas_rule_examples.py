"""Spec support: the story canvas rules on a UX map whose screens are ported to a design canvas beside it, read from
files the way a live load reads a working copy: a story map with one story of two scenarios, the UX map at
``ux/ux.json`` with one Cart screen that shows the story, and the canvas version at ``ux/design-canvas/version-1``."""

from __future__ import annotations

import json
from typing import Optional

from harness.graph.rule_fixture import RuleFixture

from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.ux import Ux

_STORY_MAP = "# (E) Choose Lines\n## (E) Choose Lines\n### (S) Customer --> Add Line To Cart\n"
_STORY_FILE = "story_tests/choose-lines/add-line-to-cart/add_line_to_cart_story.test.md"
_STORIES = (
    "# Sub-epic: Choose Lines\n\n## Story: Add Line To Cart\n\n"
    "#### Scenario: Add the first line\n\n*Given* the Customer has an empty cart\n*When* the Customer adds a line\n"
    "*Then* the cart holds one line\n\n"
    "#### Scenario: Add one more line\n\n*Given* the Customer has a cart with one line\n*When* the Customer adds one more line\n"
    "*Then* the cart holds two lines\n"
)
SCENARIOS = ("Add the first line", "Add one more line")
CANVAS_PROJECT = "ux/design-canvas/version-1/project"
SCREEN_ARTBOARD = f"{CANVAS_PROJECT}/screens/cart.dc.html"
FIXTURES_BUNDLE = f"{CANVAS_PROJECT}/fixtures/canvas-fixtures.js"
EXPLORER_PAGE = f"{CANVAS_PROJECT}/screens/explorer.dc.html"
UX_MAP = "ux/ux.json"
_FOLLOWING_PROPS = '{"story":{"editor":null},"scenario":{"editor":null},"step":{"editor":null},"go":{"editor":null}}'


def artboard(template: str, logic: str, props: str = _FOLLOWING_PROPS) -> str:
    """A screen artboard as a story canvas holds it: its x-dc template and its DCLogic."""
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<title>Cart</title>\n<script src="./support.js"></script>\n</head>\n<body>\n'
            f"<x-dc>\n<helmet><style>body{{margin:0}}</style></helmet>\n{template}\n</x-dc>\n"
            f"<script type=\"text/x-dc\" data-dc-script data-props='{props}'>\n{logic}\n</script>\n</body>\n</html>\n")


_CART = '<div class="cart"><dc-import name="shop" lines="{{shown.lines}}"></dc-import></div>'
# A screen that follows the explorer: a state for each scenario, the Then state at a Then.
FOLLOWING_SCREEN = artboard(_CART, r"""class Component extends DCLogic {
  scenarioStates() { return {"Add the first line": {"given": {"lines": 0}, "then": {"lines": 1}}, "Add one more line": {"given": {"lines": 1}, "then": {"lines": 2}}}; }
  renderVals() {
    const scenario = this.scenarioStates()[this.props.scenario || ''];
    const atThen = /(^|\n)\s*Then\b/.test(this.props.step || '');
    return { shown: scenario ? (atThen ? scenario.then : scenario.given) : { lines: 0 } };
  }
}""")
# The same screen with a state for its first scenario only.
ONE_STATE_SCREEN = FOLLOWING_SCREEN.replace(', "Add one more line": {"given": {"lines": 1}, "then": {"lines": 2}}', "")
# A screen that builds each state from the stories' fixtures.
FIXTURE_SCREEN = artboard(_CART, """class Component extends DCLogic {
  fromFixture(repositories, scenario, examples, step) { return { lines: repositories.cart.lines.length }; }
  renderVals() { return { shown: this.state || {}, scenario: this.props.scenario, step: this.props.step }; }
}""")
# A screen frozen at one state per story: it never reads the scenario or the step the explorer hands it.
FROZEN_SCREEN = artboard(_CART, "class Component extends DCLogic {\n  renderVals() { return { shown: { lines: 3 } }; }\n}",
                         '{"story":{"editor":null},"scenario":{"editor":null},"go":{"editor":null}}')
# A screenshot standing in for the screen.
SCREENSHOT_SCREEN = artboard('<div style="width: 100%"><img src="../shots/cart.png" alt="Cart"></div>',
                             "class Component extends DCLogic {\n  renderVals() { return {}; }\n}")


def fixtures_bundle(*scenarios: str) -> str:
    """A fixtures bundle that loads each of scenarios of Add Line To Cart."""
    held = {"Add Line To Cart": {name: {"cart": {"lines": []}} for name in scenarios}}
    return f"window.CanvasFixtures = {{ held: {json.dumps(held)} }};\n"


def explorer_page(*scenarios: str) -> str:
    """An explorer page listing Add Line To Cart with scenarios, each playing the cart screen."""
    listed = [{"n": name, "b": False, "p": "cart", "t": [], "f": ""} for name in scenarios]
    tree = [{"n": "Choose Lines", "u": [{"n": "Choose Lines", "s": [{"n": "Add Line To Cart", "f": "", "c": listed}]}]}]
    return f'<x-dc></x-dc>\n<script type="text/x-dc" data-dc-script>\nclass Component extends DCLogic {{\ntree() {{\nreturn {json.dumps(tree)};\n}}\n}}\n</script>\n'


def ux_map_json(prototype: str = "screens/cart.dc.html", image: str = "shots/cart.png", scenario: str = "") -> str:
    """The UX map: one Cart screen, ported to prototype, with image as its screenshot, that shows Add Line To Cart, or
    only its scenario when one is named."""
    screen = Screen("Cart", 1)
    screen.prototype = prototype
    screen.image = image
    if scenario:
        screen.show_scenario(f"Add Line To Cart › {scenario}")
    else:
        screen.show_story("Add Line To Cart")
    ux_map = UxMap.create(name="shop")
    ux_map.append_screen(screen)
    return JsonUxMap.create().copy_of(ux_map).save()


class CanvasExample:
    """The story map, the UX map, and the canvas, with files set over the defaults (a file set to None is left out),
    read by a live load of the UX practice beside Stories."""

    def __init__(self, files: dict[str, Optional[str]]) -> None:
        written = {"story-map.md": _STORY_MAP, _STORY_FILE: _STORIES, UX_MAP: ux_map_json(), EXPLORER_PAGE: explorer_page(*SCENARIOS),
                   SCREEN_ARTBOARD: FOLLOWING_SCREEN, **files}
        self.files = {path: text for path, text in written.items() if text is not None}

    def violations(self, rule) -> list[str]:
        """What the rule reports where validate runs it."""
        return RuleFixture(Ux, self.files, beside=(Stories,)).hits(rule)


class CanvasPair:
    """One story canvas rule with the canvas files it flags and the files it passes."""

    def __init__(self, rule, failing: dict[str, Optional[str]], repaired: dict[str, Optional[str]]) -> None:
        self._rule = rule
        self._failing = failing
        self._repaired = repaired

    def check(self) -> None:
        if not CanvasExample(self._failing).violations(self._rule):
            raise AssertionError(f"{self._rule.slug}: expected a finding on the failing canvas, got none")
        found = CanvasExample(self._repaired).violations(self._rule)
        if found:
            raise AssertionError(f"{self._rule.slug}: expected the repaired canvas to pass, got {found!r}")
