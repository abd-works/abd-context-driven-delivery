"""Mamba spec for the positions a prototype-state file keeps for each story's screen (PrototypeStates): the story's
position apart from its scenarios' positions, each without the settings that hold data, and each UX-map screen it has
a state for made into a StoryScreen from one screen the project configures."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.prototype_states import PrototypeStates, PrototypeStatesUnreadable
from cdd_guidance.practices.ux.model.claude_design.story_screen import PortedCanvasMarkup, StoryScreen

STATES = {
    "_about": "Each story's screen in the prototype.",
    "view-cart": {
        "start": "catalog", "demoPlans": "Atlas,Ace", "demoCartOpen": True,
        "scenarios": {"View the cart with a voucher": [
            {"start": "catalog", "demoPlans": "Atlas", "demoVoucher": "TRAVEL25"},
            {"start": "catalog", "demoPlans": "Atlas", "demoCartOpen": True}]},
    },
    "display-plans": {"start": "catalog"},
}

UX_MAP = {"name": "Shop", "screens": [
    {"name": "view-cart", "slug": "view-cart", "story_names": ["[View Cart](../story_tests/view-cart.md#story-view-cart)"]},
    {"name": "display-plans", "slug": "display-plans", "story_names": []},
    {"name": "check-order", "slug": "check-order", "story_names": ["Check Order"]},
]}

DATA_SETTINGS = {"demoPlans", "demoVoucher"}


def configured_screen() -> StoryScreen:
    return StoryScreen(title="", story="", markup=PortedCanvasMarkup("flow"), domain_input="cart", positions={},
                       root_class="pml-screen")


with description("the positions a prototype-state file keeps for each story's screen") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-prototype-states-"))
        self.file = self.root / "story-screens.json"
        self.file.write_text(json.dumps(STATES), encoding="utf-8")
        self.ux_map = self.root / "ux.json"
        self.ux_map.write_text(json.dumps(UX_MAP), encoding="utf-8")
        self.states = PrototypeStates(self.file, DATA_SETTINGS)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("one screen's state"):
        with it("should keep the story's position apart from its scenarios', without the data settings"):
            expect(self.states.story_position("view-cart")).to(equal({"start": "catalog", "demoCartOpen": True}))

        with it("should give each scenario one position per step group, without the data settings"):
            expect(self.states.positions("view-cart")).to(equal({"View the cart with a voucher": [
                {"start": "catalog"}, {"start": "catalog", "demoCartOpen": True}]}))

        with it("should give no scenario positions to a screen whose state lists no scenarios"):
            expect(self.states.positions("display-plans")).to(equal({}))

        with it("should hold no state for a slug the file does not keep, nor for a note in the file"):
            expect(self.states.story_position("check-order")).to(be_none)
            expect(self.states.story_position("_about")).to(be_none)

    with context("made into story screens for the UX map"):
        with before.each:
            self.screens = self.states.story_screens(self.ux_map, configured_screen())

        with it("should make a screen for each UX-map screen the file keeps a state for"):
            expect(sorted(self.screens)).to(equal(["display-plans", "view-cart"]))

        with it("should name the screen's story from the UX map, without its link, else from its slug"):
            expect(self.screens["view-cart"].story).to(equal("View Cart"))
            expect(self.screens["display-plans"].story).to(equal("display-plans"))

        with it("should title the screen from its slug and give its artboard on the canvas"):
            expect(self.screens["view-cart"].title).to(equal("View Cart"))
            expect(self.screens["view-cart"].artboard).to(equal("/screens/view-cart.dc.html"))

        with it("should place the screen at the file's positions and keep everything the project configured"):
            screen = self.screens["view-cart"]
            expect(screen.story_position).to(equal({"start": "catalog", "demoCartOpen": True}))
            expect(screen.positions["View the cart with a voucher"][0]).to(equal({"start": "catalog"}))
            expect(screen.root_class).to(equal("pml-screen"))
            expect(screen.markup).to(equal(PortedCanvasMarkup("flow")))

    with context("when the file cannot be read as JSON"):
        with it("should refuse it, naming the file"):
            self.file.write_text("{ not json", encoding="utf-8")
            expect(lambda: PrototypeStates(self.file, DATA_SETTINGS).story_position("view-cart")).to(
                raise_error(PrototypeStatesUnreadable, contain("story-screens.json")))
