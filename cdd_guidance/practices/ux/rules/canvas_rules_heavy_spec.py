"""The story canvas rules, at the mockup fidelity: each screen of the UX map ported to the design canvas beside it is a
prototype that follows the scenario and step the explorer hands it, with a state for every scenario it shows, and the
explorer lists each scenario once. Heavy: each example is a live load of a folder of files."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.rules import canvas_rule_examples as canvas
from cdd_guidance.practices.ux.rules.canvas_rules import (
    EveryScenarioHasAState,
    ScenarioListedOnce,
    ScreenFollowsScenario,
    ScreenIsAPrototype,
)
from cdd_guidance.practices.ux.rules.canvas_source_rules import PositionsHoldNoData, ScreenFilesFromProduction

_SCREEN = canvas.SCREEN_ARTBOARD


with description("a screen checked against the screen-is-a-prototype rule"):
    with context("whose artboard is a screenshot"):
        with it("should ask for the prototype's own screen"):
            expect(canvas.CanvasExample({_SCREEN: canvas.SCREENSHOT_SCREEN}).violations(ScreenIsAPrototype())).to(equal([
                "Screen 'Cart' is only a screenshot on the canvas (screens/cart.dc.html); port the prototype's own markup and logic."
            ]))

    with context("that has only a screenshot and no artboard on the canvas"):
        with it("should ask for the prototype's own screen"):
            found = canvas.CanvasExample({canvas.UX_MAP: canvas.ux_map_json(prototype=""), _SCREEN: None}).violations(ScreenIsAPrototype())
            expect(found).to(equal(["Screen 'Cart' shows only its screenshot (shots/cart.png) on the canvas; it has no prototype artboard."]))

    with context("that names an artboard the canvas does not hold"):
        with it("should say the artboard is missing"):
            expect(canvas.CanvasExample({_SCREEN: None}).violations(ScreenIsAPrototype())).to(equal([
                "Screen 'Cart' names the prototype screens/cart.dc.html, which the canvas version does not hold."
            ]))

    with context("whose artboard is the ported prototype"):
        with it("should pass"):
            expect(canvas.CanvasExample({}).violations(ScreenIsAPrototype())).to(equal([]))

    with context("on a UX map with no design canvas beside it"):
        with it("should pass, since the screens are not ported yet"):
            files = {canvas.EXPLORER_PAGE: None, _SCREEN: None}
            expect(canvas.CanvasExample(files).violations(ScreenIsAPrototype())).to(equal([]))


with description("a screen checked against the screen-follows-scenario rule"):
    with context("frozen at one state, never reading the scenario or the step"):
        with before.each:
            self.found = canvas.CanvasExample({_SCREEN: canvas.FROZEN_SCREEN}).violations(ScreenFollowsScenario())

        with it("should name the prop it does not declare"):
            expect(self.found[0]).to(contain("does not declare step in data-props"))

        with it("should name the props its logic never reads"):
            expect(self.found[0]).to(contain("its logic never reads props.scenario, props.step"))

    with context("that reads the scenario and the step"):
        with it("should pass"):
            expect(canvas.CanvasExample({}).violations(ScreenFollowsScenario())).to(equal([]))


with description("a screen checked against the every-scenario-has-a-state rule"):
    with context("with a state for one of its story's two scenarios"):
        with it("should name the scenario with no state"):
            expect(canvas.CanvasExample({_SCREEN: canvas.ONE_STATE_SCREEN}).violations(EveryScenarioHasAState())).to(equal([
                "Screen 'Cart' has no state or fixture for: Add Line To Cart › Add one more line."
            ]))

    with context("with a state for every scenario"):
        with it("should pass"):
            expect(canvas.CanvasExample({}).violations(EveryScenarioHasAState())).to(equal([]))

    with context("that shows one scenario, with no state for it"):
        with it("should name that scenario"):
            files = {canvas.UX_MAP: canvas.ux_map_json(scenario="Add one more line"), _SCREEN: canvas.ONE_STATE_SCREEN}
            expect(canvas.CanvasExample(files).violations(EveryScenarioHasAState())).to(equal([
                "Screen 'Cart' has no state or fixture for: Add Line To Cart › Add one more line."
            ]))

    with context("that shows one scenario, with a state for it"):
        with it("should pass, leaving the story's other scenario to the screens that show it"):
            files = {canvas.UX_MAP: canvas.ux_map_json(scenario="Add the first line"), _SCREEN: canvas.ONE_STATE_SCREEN}
            expect(canvas.CanvasExample(files).violations(EveryScenarioHasAState())).to(equal([]))

    with context("that builds its states from a fixtures bundle holding every scenario"):
        with it("should pass"):
            files = {_SCREEN: canvas.FIXTURE_SCREEN, canvas.FIXTURES_BUNDLE: canvas.fixtures_bundle(*canvas.SCENARIOS)}
            expect(canvas.CanvasExample(files).violations(EveryScenarioHasAState())).to(equal([]))

    with context("that builds its states from a fixtures bundle missing a scenario"):
        with it("should name the scenario the bundle cannot load"):
            files = {_SCREEN: canvas.FIXTURE_SCREEN, canvas.FIXTURES_BUNDLE: canvas.fixtures_bundle(canvas.SCENARIOS[0])}
            expect(canvas.CanvasExample(files).violations(EveryScenarioHasAState())).to(equal([
                "Screen 'Cart' has no state or fixture for: Add Line To Cart › Add one more line."
            ]))


with description("a UX map checked against the scenario-listed-once rule"):
    with context("whose canvas explorer lists a scenario twice under one story"):
        with it("should name the scenario listed twice"):
            files = {canvas.EXPLORER_PAGE: canvas.explorer_page(*canvas.SCENARIOS, canvas.SCENARIOS[0])}
            expect(canvas.CanvasExample(files).violations(ScenarioListedOnce())).to(equal([
                "The story explorer lists Add Line To Cart › Add the first line 2 times."
            ]))

    with context("whose canvas explorer lists each scenario once"):
        with it("should pass"):
            expect(canvas.CanvasExample({}).violations(ScenarioListedOnce())).to(equal([]))


with description("a UX map checked against the screen-files-from-production rule"):
    with context("whose screen loads a script copied from a prototype folder"):
        with it("should name the file, the screen, and where it was copied from"):
            files = {_SCREEN: canvas.loading_screen("../flow.js"), canvas.SCREEN_SOURCES: canvas.screen_sources({"flow.js": "ux/prototype/flow.js"})}
            expect(canvas.CanvasExample(files).violations(ScreenFilesFromProduction())).to(equal([
                "Screens cart load flow.js, copied from ux/prototype/flow.js, which is not the product's code; "
                "load the production file, or a converted copy of it, instead."
            ]))

    with context("whose screen loads a script nobody recorded a source for"):
        with it("should name the file as untraced"):
            found = canvas.CanvasExample({_SCREEN: canvas.loading_screen("../flow.js")}).violations(ScreenFilesFromProduction())
            expect(found).to(equal(["Screens cart load flow.js, which screen-sources.json does not trace to any source; "
                                    "copy it from the product's code through the screen's markup files and render again."]))

    with context("whose screen loads files copied from the product's code, a folder of them among them"):
        with it("should pass"):
            files = {_SCREEN: canvas.loading_screen("../ds/app/bundle.js", "../ds/app/tokens.css"),
                     canvas.SCREEN_SOURCES: canvas.screen_sources({"ds/app": "packages/app/assets"})}
            expect(canvas.CanvasExample(files).violations(ScreenFilesFromProduction())).to(equal([]))


with description("a UX map checked against the positions-hold-no-data rule"):
    with context("whose screen keeps a code typed into a position"):
        with it("should name the screen, the setting, and the scenario with its value"):
            files = {_SCREEN: canvas.positioned_screen({"Add the first line": [{"page": "catalog", "demoCode": "123456"}]}),
                     canvas.COMPONENT_ARTBOARD: canvas.SHOP_COMPONENT}
            expect(canvas.CanvasExample(files).violations(PositionsHoldNoData())).to(equal([
                'Screen cart keeps demoCode as a position, but it holds example data in Add the first line ("123456"); '
                "give the value through the scenario's fixtures."
            ]))

    with context("whose screen keeps a value its component does not offer"):
        with it("should name it"):
            files = {_SCREEN: canvas.positioned_screen({"Add the first line": [{"page": "checkout"}]}), canvas.COMPONENT_ARTBOARD: canvas.SHOP_COMPONENT}
            expect(len(canvas.CanvasExample(files).violations(PositionsHoldNoData()))).to(equal(1))

    with context("whose screen keeps only the component's options and true or false"):
        with it("should pass"):
            files = {_SCREEN: canvas.positioned_screen({"Add the first line": [{"page": "catalog"}, {"page": "cart", "demoCartOpen": True}]}),
                     canvas.COMPONENT_ARTBOARD: canvas.SHOP_COMPONENT}
            expect(canvas.CanvasExample(files).violations(PositionsHoldNoData())).to(equal([]))

    with context("whose project accepts a text setting as a position by name"):
        with it("should pass"):
            files = {_SCREEN: canvas.positioned_screen({"Add the first line": [{"page": "catalog", "theme": "dark"}]}),
                     canvas.COMPONENT_ARTBOARD: canvas.SHOP_COMPONENT, canvas.ACCEPTED_POSITIONS: '{"accepted": ["theme"]}'}
            expect(canvas.CanvasExample(files).violations(PositionsHoldNoData())).to(equal([]))
