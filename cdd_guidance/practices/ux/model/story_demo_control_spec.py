"""StoryDemoControl extends Control - JSON, and the HTML its page control writes."""

import sys
from pathlib import Path

from expects import be_a, equal, expect
from mamba import description, it

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen, StoryDemoControl, StoryStep
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.html.nodes import HtmlControl, HtmlStoryDemoControl
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import made


with description("StoryDemoControl"):
    with it("should extend Control with story_steps"):
        control = made(StoryDemoControl, "Create Character", 0, control_type="button", label="Create Character", bound_field="character", story_steps=StoryStep.from_values([{"kind": "when", "label": "the Player creates a Character"}]))
        expect(control).to(be_a(Control))
        expect(control.bound_field).to(equal("character"))
        expect(control.story_steps[0]).to(equal(StoryStep("when", "the Player creates a Character")))

    with it("should round-trip story_steps through JSON"):
        ux_map = UxMap.create()
        ux_map.name = "demo"
        screen = made(Screen, "character sheet", 0, slug="character-sheet")
        region = made(Region, "verbs", 0, area="body")
        region.append_control(
            made(StoryDemoControl, "Create Character", 0, control_type="button", label="Create Character", bound_field="character", story_steps=StoryStep.from_values([{"kind": "when", "label": "the Player creates a Character"}]))
        )
        screen.append_region(region)
        ux_map.append_screen(screen)

        parsed = JsonUxMap.create().parse(JsonUxMap.create().render(ux_map))
        control = parsed.screens[0].regions[0].controls[0]
        expect(control).to(be_a(StoryDemoControl))
        expect(control.story_steps[0].label).to(equal("the Player creates a Character"))
        expect(control.bound_field).to(equal("character"))

    with it("should emit data-bound-field and data-story-steps in HTML"):
        control = made(HtmlStoryDemoControl, "Create Character", 0, control_type="button", label="Create Character", bound_field="character", story_steps=StoryStep.from_values([{"kind": "when", "label": "the Player creates a Character"}]))
        html = control.html()
        expect('data-bound-field="character"' in html).to(equal(True))
        expect("data-story-steps=" in html).to(equal(True))
        expect("the Player creates a Character" in html).to(equal(True))

    with it("should omit data-story-steps for vanilla Control"):
        control = made(HtmlControl, "Done", 0, control_type="button", label="Done", bound_field="")
        html = control.html()
        expect("data-story-steps" in html).to(equal(False))

    with it("should emit generic bound-list Interactive attrs"):
        control = made(HtmlStoryDemoControl, "Products", 0, control_type="bound-list", label="Products", bound_field="catalog.products", story_steps=StoryStep.from_values([]), set_input="product", item_story_steps=StoryStep.from_values([{"kind": "when", "label": "the Customer selects a Product from the Product Catalog"}]), item_value="name", item_label="{name} . {unitPrice}")
        html = control.html()
        expect("data-bound-list" in html).to(equal(True))
        expect('data-bound-field="catalog.products"' in html).to(equal(True))
        expect('data-set-input="product"' in html).to(equal(True))
        expect("data-item-story-steps=" in html).to(equal(True))
        expect('data-item-value="name"' in html).to(equal(True))

    with it("should emit data-input-field for number controls"):
        control = made(HtmlStoryDemoControl, "Quantity", 0, control_type="number", label="quantity", bound_field="", story_steps=StoryStep.from_values([]), set_input="quantity")
        html = control.html()
        expect('data-input-field="quantity"' in html).to(equal(True))
        expect('type="number"' in html).to(equal(True))

    with it("should round-trip set_input and item_story_steps through JSON"):
        ux_map = UxMap.create()
        ux_map.name = "demo"
        screen = made(Screen, "catalog", 0, slug="catalog")
        region = made(Region, "list", 0, area="body")
        region.append_control(
            made(StoryDemoControl, "Products", 0, control_type="bound-list", label="Products", bound_field="items", story_steps=StoryStep.from_values([]), set_input="product", item_story_steps=StoryStep.from_values([{"kind": "when", "label": "selects a Product"}]), item_value="name", item_label="{name}")
        )
        screen.append_region(region)
        ux_map.append_screen(screen)
        parsed = JsonUxMap.create().parse(JsonUxMap.create().render(ux_map))
        control = parsed.screens[0].regions[0].controls[0]
        expect(control).to(be_a(StoryDemoControl))
        expect(control.set_input).to(equal("product"))
        expect(control.item_story_steps[0].label).to(equal("selects a Product"))
        expect(control.item_value).to(equal("name"))
        expect(control.item_label).to(equal("{name}"))
