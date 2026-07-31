"""StoryDemoControl extends Control - JSON + HTML emit."""

import sys
from pathlib import Path

from expects import be_a, equal, expect
from mamba import description, it

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.document.json.nodes import JsonUxMap
from context_tools.ux.ux_model.nodes import Control, Region, Screen, StoryDemoControl
from context_tools.ux.ux_model.ux_map import UxMap
from context_tools.ux.web.html.nodes import _render_control


with description("StoryDemoControl"):
    with it("should extend Control with story_steps"):
        control = StoryDemoControl(
            "Create Character",
            0,
            "button",
            "Create Character",
            "character",
            [{"kind": "when", "label": "the Player creates a Character"}],
        )
        expect(control).to(be_a(Control))
        expect(control.bound_field).to(equal("character"))
        expect(control.story_steps[0]["kind"]).to(equal("when"))

    with it("should round-trip story_steps through JSON"):
        ux_map = UxMap()
        ux_map.name = "demo"
        screen = Screen("character sheet", 0, "character-sheet")
        region = Region("verb row", 0, "body")
        region.append_control(
            StoryDemoControl(
                "Create Character",
                0,
                "button",
                "Create Character",
                "character",
                [{"kind": "when", "label": "the Player creates a Character"}],
            )
        )
        screen.append_region(region)
        ux_map.append_screen(screen)

        parsed = JsonUxMap.parse(JsonUxMap.render(ux_map))
        control = parsed.screens[0].regions[0].controls[0]
        expect(control).to(be_a(StoryDemoControl))
        expect(control.story_steps[0]["label"]).to(
            equal("the Player creates a Character")
        )
        expect(control.bound_field).to(equal("character"))

    with it("should emit data-bound-field and data-story-steps in HTML"):
        control = StoryDemoControl(
            "Create Character",
            0,
            "button",
            "Create Character",
            "character",
            [{"kind": "when", "label": "the Player creates a Character"}],
        )
        html = _render_control(control)
        expect('data-bound-field="character"' in html).to(equal(True))
        expect("data-story-steps=" in html).to(equal(True))
        expect("the Player creates a Character" in html).to(equal(True))

    with it("should omit data-story-steps for vanilla Control"):
        control = Control("Done", 0, "button", "Done", "")
        html = _render_control(control)
        expect("data-story-steps" in html).to(equal(False))

    with it("should emit generic bound-list Interactive attrs"):
        control = StoryDemoControl(
            "Products",
            0,
            "bound-list",
            "Products",
            "catalog.products",
            [],
            "product",
            [{"kind": "when", "label": "the Customer selects a Product from the Product Catalog"}],
            "name",
            "{name} . {unitPrice}",
        )
        html = _render_control(control)
        expect("data-bound-list" in html).to(equal(True))
        expect('data-bound-field="catalog.products"' in html).to(equal(True))
        expect('data-set-input="product"' in html).to(equal(True))
        expect("data-item-story-steps=" in html).to(equal(True))
        expect('data-item-value="name"' in html).to(equal(True))

    with it("should emit data-input-field for number controls"):
        control = StoryDemoControl(
            "Quantity",
            0,
            "number",
            "quantity",
            "",
            [],
            "quantity",
        )
        html = _render_control(control)
        expect('data-input-field="quantity"' in html).to(equal(True))
        expect('type="number"' in html).to(equal(True))

    with it("should round-trip set_input and item_story_steps through JSON"):
        ux_map = UxMap()
        ux_map.name = "demo"
        screen = Screen("catalog", 0, "catalog")
        region = Region("list", 0, "body")
        region.append_control(
            StoryDemoControl(
                "Products",
                0,
                "bound-list",
                "Products",
                "items",
                [],
                "product",
                [{"kind": "when", "label": "selects a Product"}],
                "name",
                "{name}",
            )
        )
        screen.append_region(region)
        ux_map.append_screen(screen)
        parsed = JsonUxMap.parse(JsonUxMap.render(ux_map))
        control = parsed.screens[0].regions[0].controls[0]
        expect(control).to(be_a(StoryDemoControl))
        expect(control.set_input).to(equal("product"))
        expect(control.item_story_steps[0]["label"]).to(equal("selects a Product"))
        expect(control.item_value).to(equal("name"))
        expect(control.item_label).to(equal("{name}"))
