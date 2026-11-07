"""A full UX map for the format round-trip specs, and an outline that compares two maps field by field."""

from __future__ import annotations

from typing import Any

from cdd_guidance.practices.ux.model.nodes import (
    ContentType,
    Control,
    Interaction,
    NavComponent,
    Region,
    Screen,
    StoryDemoControl,
    Transition,
)
from cdd_guidance.practices.ux.model.ux_map import UxMap


class OrderingMap:
    """Catalog and Cart screens, a Cart tab that shares the Cart chrome, and every kind of link between them."""

    def build(self, ux_map: UxMap) -> UxMap:
        ux_map.name = "ordering"
        ux_map.scope = "Place New Order"
        ux_map.story_references = ["stories/place_order.js"]
        ux_map.object_references = ["domain/order.js"]
        ux_map.context.notes = ["Keep chrome shared across tabs --> always"]
        ux_map.context.invariants = ["Tab states are separate screens"]
        catalog, cart, saved = self._screens(ux_map)
        catalog.append_region(self._catalog_region(cart))
        ux_map.transitions.append(Transition("opens cart", 0, catalog, cart, "opens cart", "action"))
        content_type = ContentType("Product", 0, "Catalog > Product")
        content_type.key_actions = ["add to cart"]
        ux_map.content_types.append(content_type)
        nav = NavComponent("Top nav", 0, "top nav")
        nav.destinations = [catalog, cart]
        ux_map.nav_components.append(nav)
        return ux_map

    def _screens(self, ux_map: UxMap) -> tuple[Screen, Screen, Screen]:
        catalog = Screen("Catalog", 0, "catalog", "stack", "Browse products")
        catalog.attach_story_name("Browse Product Catalog")
        catalog.attach_scenario_name("Browse Product Catalog › Products are listed")
        catalog.attach_step_name("Browse Product Catalog › Products are listed › the Customer opens the catalog")
        catalog.attach_domain_term("Product")
        catalog.domain_concepts = ["Catalog"]
        catalog.image = "screens/catalog.png"
        catalog.prototype = "screens/catalog.dc.html"
        cart = Screen("Cart", 1, "cart", "sidebar")
        saved = Screen("Cart - Saved", 2, chrome_of=cart)
        saved.inactive_tabs = ["Current"]
        for screen in (catalog, cart, saved):
            ux_map.append_screen(screen)
        return catalog, cart, saved

    def _catalog_region(self, cart: Screen) -> Region:
        region = Region("product list", 0, "body")
        browse = Control("Browse", 0, "button", "Browse <all>", "")
        browse.states = ["primary"]
        browse.append_interaction(Interaction("open cart", 0, "click", "shows the cart", cart))
        region.append_control(browse)
        region.append_control(StoryDemoControl(
            "Products", 1, "bound-list", "Products", "catalog.products",
            [{"kind": "given", "label": "the catalog lists Products"}],
            "product",
            [{"kind": "when", "label": "the Customer selects a Product"}],
            "name",
            "{name}",
        ))
        return region


def outline(ux_map: UxMap) -> dict[str, Any]:
    """Every field of the map and its nodes, with each link to a screen written as that screen's name."""
    return {
        "name": ux_map.name,
        "scope": ux_map.scope,
        "story_references": ux_map.story_references.as_list(),
        "object_references": ux_map.object_references.as_list(),
        "notes": list(ux_map.context.notes),
        "invariants": list(ux_map.context.invariants),
        "screens": [_screen_outline(screen) for screen in ux_map.screens],
        "transitions": [
            (t.name, _name(t.from_screen), _name(t.to_screen), t.trigger, t.nav_type) for t in ux_map.transitions
        ],
        "content_types": [(c.name, c.hierarchy, list(c.key_actions)) for c in ux_map.content_types],
        "nav_components": [(n.name, n.ux_type, [s.name for s in n.destinations]) for n in ux_map.nav_components],
    }


def _screen_outline(screen: Screen) -> dict[str, Any]:
    return {
        "fields": (screen.name, screen.slug, screen.layout, screen.description, _name(screen.chrome_of),
                   screen.image, screen.prototype),
        "lists": (screen.inactive_tabs, screen.story_names, screen.scenario_names, screen.step_names,
                  screen.domain_terms, screen.domain_concepts),
        "regions": [
            (region.name, region.area, [_control_outline(control) for control in region.controls])
            for region in screen.regions
        ],
    }


def _control_outline(control: Control) -> tuple:
    interactions = [(i.name, i.trigger, i.effect, _name(i.destination)) for i in control.interactions]
    fields = (type(control).__name__, control.name, control.control_type, control.label, control.bound_field,
              list(control.states), interactions)
    if not isinstance(control, StoryDemoControl):
        return fields
    return fields + (control.story_steps, control.set_input, control.item_story_steps, control.item_value,
                     control.item_label)


def _name(screen: Screen | None) -> str:
    return screen.name if screen is not None else ""
