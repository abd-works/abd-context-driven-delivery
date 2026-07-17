"""Concrete UX node types: Screen, Region, Control, and peers."""

from __future__ import annotations

from typing import List

from .update_report import ChildCollectionPair
from .ux_node import UxNode


class Interaction(UxNode):
    _semantic_type_name = "Interaction"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        trigger: str = "",
        effect: str = "",
        destination_screen: str = "",
    ) -> None:
        super().__init__(name, sequential_order)
        self.trigger = trigger or name
        self.effect = effect
        self.destination_screen = destination_screen

    def update_self(self, source: "Interaction") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.trigger = source.trigger
        self.effect = source.effect
        self.destination_screen = source.destination_screen

    def child_collections(self, source: "Interaction") -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {
            "trigger": self.trigger,
            "effect": self.effect,
            "destination_screen": self.destination_screen,
        }


class Control(UxNode):
    _semantic_type_name = "Control"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        control_type: str = "",
        label: str = "",
        bound_field: str = "",
    ) -> None:
        super().__init__(name, sequential_order)
        self.control_type = control_type
        self.label = label or name
        self.bound_field = bound_field
        self.states: List[str] = []
        self.interactions: List[Interaction] = []

    def update_self(self, source: "Control") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.control_type = source.control_type
        self.label = source.label
        self.bound_field = source.bound_field
        self.states = list(source.states)

    def child_collections(self, source: "Control") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.interactions,
                source_children=source.interactions,
                create_child=self.create_child_interaction,
            )
        ]

    def create_child_interaction(self, source: Interaction) -> Interaction:
        return Interaction(
            source.name,
            source.sequential_order,
            source.trigger,
            source.effect,
            source.destination_screen,
        )

    def append_interaction(self, interaction: Interaction) -> None:
        self.interactions.append(interaction)
        self._renumber(self.interactions)

    def snapshot_fields(self) -> dict:
        return {
            "control_type": self.control_type,
            "label": self.label,
            "bound_field": self.bound_field,
            "states": list(self.states),
        }


class Region(UxNode):
    _semantic_type_name = "Region"

    def __init__(self, name: str, sequential_order: int, slot: str = "") -> None:
        super().__init__(name, sequential_order)
        self.slot = slot
        self.controls: List[Control] = []

    def update_self(self, source: "Region") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.slot = source.slot

    def child_collections(self, source: "Region") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.controls,
                source_children=source.controls,
                create_child=self.create_child_control,
            )
        ]

    def create_child_control(self, source: Control) -> Control:
        return Control(
            source.name,
            source.sequential_order,
            source.control_type,
            source.label,
            source.bound_field,
        )

    def append_control(self, control: Control) -> None:
        self.controls.append(control)
        self._renumber(self.controls)

    def snapshot_fields(self) -> dict:
        return {"slot": self.slot}


class Screen(UxNode):
    _semantic_type_name = "Screen"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        slug: str = "",
        layout: str = "",
        description: str = "",
        chrome_of: str = "",
    ) -> None:
        super().__init__(name, sequential_order)
        self.slug = slug or _slugify(name)
        self.layout = layout
        self.description = description
        self.chrome_of = chrome_of
        self.inactive_tabs: List[str] = []
        self.story_names: List[str] = []
        self.domain_terms: List[str] = []
        self.domain_concepts: List[str] = []
        self.regions: List[Region] = []

    def update_self(self, source: "Screen") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.slug = source.slug
        self.layout = source.layout
        self.description = source.description
        self.chrome_of = source.chrome_of
        self.inactive_tabs = list(source.inactive_tabs)
        self.story_names = list(source.story_names)
        self.domain_terms = list(source.domain_terms)
        self.domain_concepts = list(source.domain_concepts)

    def child_collections(self, source: "Screen") -> List[ChildCollectionPair]:
        return [
            ChildCollectionPair(
                self_children=self.regions,
                source_children=source.regions,
                create_child=self.create_child_region,
            )
        ]

    def create_child_region(self, source: Region) -> Region:
        return Region(source.name, source.sequential_order, source.slot)

    def append_region(self, region: Region) -> None:
        self.regions.append(region)
        self._renumber(self.regions)

    def apply_layout(self, layout_id: str, *, seed_regions: bool = True) -> None:
        """Set layout from the thin catalog; optionally seed empty regions from slots."""
        from .layouts import resolve_layout

        template = resolve_layout(layout_id)
        if template is None:
            self.layout = (layout_id or "").strip()
            return
        self.layout = template.id
        if seed_regions and not self.regions:
            for index, slot in enumerate(template.slots):
                self.append_region(Region(slot, index, slot))

    def attach_story_name(self, story_name: str) -> None:
        if story_name and story_name not in self.story_names:
            self.story_names.append(story_name)

    def attach_domain_term(self, term: str) -> None:
        if term and term not in self.domain_terms:
            self.domain_terms.append(term)

    def snapshot_fields(self) -> dict:
        return {
            "slug": self.slug,
            "layout": self.layout,
            "description": self.description,
            "chrome_of": self.chrome_of,
            "inactive_tabs": list(self.inactive_tabs),
            "story_names": list(self.story_names),
            "domain_terms": list(self.domain_terms),
            "domain_concepts": list(self.domain_concepts),
        }


class UxComponent(UxNode):
    """First-class UX structural peer on the map (transition, content type, nav)."""

    _semantic_type_name = "UxComponent"

    def update_self(self, source: "UxComponent") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order

    def child_collections(self, source: "UxComponent") -> List[ChildCollectionPair]:
        return []


class Transition(UxComponent):
    _semantic_type_name = "Transition"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        from_screen: str = "",
        to_screen: str = "",
        trigger: str = "",
        nav_type: str = "action",
    ) -> None:
        super().__init__(name, sequential_order)
        self.from_screen = from_screen
        self.to_screen = to_screen
        self.trigger = trigger or name
        self.nav_type = nav_type

    def update_self(self, source: "Transition") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.from_screen = source.from_screen
        self.to_screen = source.to_screen
        self.trigger = source.trigger
        self.nav_type = source.nav_type

    def child_collections(self, source: "Transition") -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {
            "from_screen": self.from_screen,
            "to_screen": self.to_screen,
            "trigger": self.trigger,
            "nav_type": self.nav_type,
        }


class ContentType(UxComponent):
    _semantic_type_name = "ContentType"

    def __init__(self, name: str, sequential_order: int, hierarchy: str = "") -> None:
        super().__init__(name, sequential_order)
        self.hierarchy = hierarchy
        self.key_actions: List[str] = []

    def update_self(self, source: "ContentType") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.hierarchy = source.hierarchy
        self.key_actions = list(source.key_actions)

    def child_collections(self, source: "ContentType") -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {"hierarchy": self.hierarchy, "key_actions": list(self.key_actions)}


class NavComponent(UxComponent):
    _semantic_type_name = "NavComponent"

    def __init__(self, name: str, sequential_order: int, ux_type: str = "") -> None:
        super().__init__(name, sequential_order)
        self.ux_type = ux_type
        self.destinations: List[str] = []

    def update_self(self, source: "NavComponent") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.ux_type = source.ux_type
        self.destinations = list(source.destinations)

    def child_collections(self, source: "NavComponent") -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {"ux_type": self.ux_type, "destinations": list(self.destinations)}


class UxContext(UxNode):
    """Optional notes — invariants / thinking not on screens."""

    _semantic_type_name = "UxContext"

    def __init__(self, name: str = "context", sequential_order: int = 0) -> None:
        super().__init__(name, sequential_order)
        self.notes: List[str] = []
        self.invariants: List[str] = []

    def update_self(self, source: "UxContext") -> None:
        self.name = source.name
        self.sequential_order = source.sequential_order
        self.notes = list(source.notes)
        self.invariants = list(source.invariants)

    def child_collections(self, source: "UxContext") -> List[ChildCollectionPair]:
        return []

    def snapshot_fields(self) -> dict:
        return {"notes": list(self.notes), "invariants": list(self.invariants)}


def _slugify(name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name.strip())
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")
