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
from cdd_guidance.practices.ux.model.nodes import story_steps_from


def made(node_type: type, name: str, sequential_order: int, graph: Any = None, **fields: Any) -> Any:
    """A UX node of node_type called name at sequential_order, on graph, with each of fields set on it as a format
    sets them once the node is made."""
    node = node_type(name, sequential_order, graph)
    for field, value in fields.items():
        setattr(node, field, value)
    return node


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
        ux_map.transitions.append(made(Transition, "opens cart", 0, from_screen=catalog, to_screen=cart, trigger="opens cart", nav_type="action"))
        content_type = made(ContentType, "Product", 0, hierarchy="Catalog > Product")
        content_type.key_actions = ["add to cart"]
        ux_map.content_types.append(content_type)
        nav = made(NavComponent, "Top nav", 0, ux_type="top nav")
        nav.destinations = [catalog, cart]
        ux_map.nav_components.append(nav)
        return ux_map

    def _screens(self, ux_map: UxMap) -> tuple[Screen, Screen, Screen]:
        catalog = made(Screen, "Catalog", 0, slug="catalog", layout="stack", description="Browse products")
        catalog.show_story("Browse Product Catalog")
        catalog.show_scenario("Browse Product Catalog › Products are listed")
        catalog.show_step("Browse Product Catalog › Products are listed › the Customer opens the catalog")
        catalog.attach_domain_term("Product")
        catalog.domain_concepts = ["Catalog"]
        catalog.image = "screens/catalog.png"
        catalog.prototype = "screens/catalog.dc.html"
        cart = made(Screen, "Cart", 1, slug="cart", layout="sidebar")
        saved = made(Screen, "Cart - Saved", 2, chrome_of=cart)
        saved.inactive_tabs = ["Current"]
        for screen in (catalog, cart, saved):
            ux_map.append_screen(screen)
        return catalog, cart, saved

    def _catalog_region(self, cart: Screen) -> Region:
        region = made(Region, "product list", 0, area="body")
        browse = made(Control, "Browse", 0, control_type="button", label="Browse <all>", bound_field="")
        browse.states = ["primary"]
        browse.append_interaction(made(Interaction, "open cart", 0, trigger="click", effect="shows the cart", destination=cart))
        region.append_control(browse)
        region.append_control(made(StoryDemoControl, "Products", 1, control_type="bound-list", label="Products", bound_field="catalog.products", story_steps=story_steps_from([{"kind": "given", "label": "the catalog lists Products"}]), set_input="product", item_story_steps=story_steps_from([{"kind": "when", "label": "the Customer selects a Product"}]), item_value="name", item_label="{name}"))
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
        "lists": (screen.inactive_tabs, screen.story_keys, screen.scenario_keys, screen.step_keys,
                  screen.domain_terms, screen.domain_concepts),
        "regions": [
            (region.name, region.area, [_control_outline(control) for control in region.controls])
            for region in screen.regions
        ],
    }


def _control_outline(control: Control) -> tuple:
    interactions = [(i.name, i.trigger, i.effect, _name(i.destination)) for i in control.interactions]
    fields = (control.semantic_type(), control.name, control.control_type, control.label, control.bound_field,
              list(control.states), interactions)
    if not isinstance(control, StoryDemoControl):
        return fields
    return fields + (control.story_steps, control.set_input, control.item_story_steps, control.item_value,
                     control.item_label)


def _name(screen: Screen | None) -> str:
    return screen.name if screen is not None else ""
