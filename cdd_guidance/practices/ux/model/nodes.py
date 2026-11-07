"""Concrete UX node types: Screen, Region, Control, and peers.

Every node is built on, or moved onto, its map's graph: the lists that hold a node's children record the graph edge
when a child is appended. Links from one screen to another hold the Screen itself, so renaming a screen keeps them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Optional

from harness.name.name import Name
from harness.graph.bound_node import BoundChildren
from harness.graph.graph import Graph

from .ux_node import UxNode


@dataclass(frozen=True)
class StoryStep:
    """A story step a control runs in the mockup: its kind (given, when, then) and the step text Stories wrote."""

    kind: str = ""
    label: str = ""

    @classmethod
    def from_value(cls, value: "StoryStep | Mapping[str, Any]") -> "StoryStep":
        """A step from a file's ``{kind, label}`` object, or the step itself."""
        if isinstance(value, StoryStep):
            return value
        return cls(str(value.get("kind", "") or ""), str(value.get("label", "") or ""))

    def as_dict(self) -> dict:
        return {"kind": self.kind, "label": self.label}


def story_steps_from(values: Iterable["StoryStep | Mapping[str, Any]"] | None) -> List[StoryStep]:
    return [StoryStep.from_value(value) for value in values or ()]


class Interaction(UxNode):
    _semantic_type_name = "Interaction"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        trigger: str = "",
        effect: str = "",
        destination: Optional["Screen"] = None,
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.trigger = trigger or name
        self.effect = effect
        self.destination = destination


class Control(UxNode):
    _semantic_type_name = "Control"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        control_type: str = "",
        label: str = "",
        bound_field: str = "",
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.control_type = control_type
        self.label = label or name
        self.bound_field = bound_field
        self.states: List[str] = []
        self.interactions = BoundChildren(self, "interactions")

    def append_interaction(self, interaction: Interaction) -> None:
        self.interactions.append(interaction)
        self._renumber(self.interactions)


class StoryDemoControl(Control):
    """A control that runs story steps in the Story Demo's Play and Interactive modes.

    Interactive extras (domain-agnostic, not catalog or cart specific):
    - set_input: the scenario input this control's value fills (a list pick or the control itself)
    - item_story_steps: the When each item of a bound list runs (its labels fill {name} / {product})
    - item_value / item_label: which item field is the picked value, and the template each item shows
    """

    _semantic_type_name = "StoryDemoControl"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        control_type: str = "",
        label: str = "",
        bound_field: str = "",
        story_steps: Iterable["StoryStep | Mapping[str, Any]"] | None = None,
        set_input: str = "",
        item_story_steps: Iterable["StoryStep | Mapping[str, Any]"] | None = None,
        item_value: str = "",
        item_label: str = "",
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, control_type, label, bound_field, graph)
        self.story_steps: List[StoryStep] = story_steps_from(story_steps)
        self.set_input = set_input or ""
        self.item_story_steps: List[StoryStep] = story_steps_from(item_story_steps)
        self.item_value = item_value or ""
        self.item_label = item_label or ""


class Region(UxNode):
    _semantic_type_name = "Region"

    def __init__(self, name: str, sequential_order: int, area: str = "", graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.area = area
        self.controls = BoundChildren(self, "controls")

    def append_control(self, control: Control) -> None:
        self.controls.append(control)
        self._renumber(self.controls)


class Screen(UxNode):
    """One screen of the map.

    Its story links are names written the way Stories keys them: a story by its name, a scenario as
    ``Story › Scenario``, a step as ``Story › Scenario › Step``. Each story, scenario, and step on the same graph whose
    key a screen lists records ``shownOn`` that screen, and the screen records ``shows`` each story.
    """

    _semantic_type_name = "Screen"
    _schema_edge_fields = UxNode._schema_edge_fields | {"story_names", "scenario_names", "step_names"}

    def __init__(
        self,
        name: str,
        sequential_order: int,
        slug: str = "",
        layout: str = "",
        description: str = "",
        chrome_of: Optional["Screen"] = None,
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.slug = slug or Name(name).title_slug
        self.layout = layout
        self.description = description
        self.chrome_of = chrome_of
        self.inactive_tabs: List[str] = []
        self.story_names: List[str] = []
        self.scenario_names: List[str] = []
        self.step_names: List[str] = []
        self.domain_terms: List[str] = []
        self.domain_concepts: List[str] = []
        self.image = ""
        self.prototype = ""
        self.regions = BoundChildren(self, "regions")

    def append_region(self, region: Region) -> None:
        self.regions.append(region)
        self._renumber(self.regions)

    def apply_layout(self, layout_id: str) -> None:
        """Set the layout id (free text - e.g. one of specifications/generic/*).

        Look at the matching `specifications/generic/<layout_id>.md` (or a
        branded sibling folder under `specifications/`, e.g. `abd-works/`)
        for that layout's areas and append real `Region`s yourself; this does
        not seed placeholder regions.
        """
        self.layout = (layout_id or "").strip()

    def attach_story_name(self, story_name: str) -> None:
        self._attach(self.story_names, story_name)

    def attach_scenario_name(self, scenario_name: str) -> None:
        """A scenario this screen shows, named ``Story › Scenario``; the scenario's ``shownOn`` edge follows it."""
        self._attach(self.scenario_names, scenario_name)

    def attach_step_name(self, step_name: str) -> None:
        """A step this screen shows, named ``Story › Scenario › Step``; the step's ``shownOn`` edge follows it."""
        self._attach(self.step_names, step_name)

    def attach_domain_term(self, term: str) -> None:
        if term and term not in self.domain_terms:
            self.domain_terms.append(term)

    def _attach(self, names: List[str], name: str) -> None:
        if not name or name in names:
            return
        names.append(name)
        self._sync_schema_edges()


class UxComponent(UxNode):
    """A structural peer of the screens on the map: a transition, a content type, or a nav component."""

    _semantic_type_name = "UxComponent"


class Transition(UxComponent):
    _semantic_type_name = "Transition"

    def __init__(
        self,
        name: str,
        sequential_order: int,
        from_screen: Optional[Screen] = None,
        to_screen: Optional[Screen] = None,
        trigger: str = "",
        nav_type: str = "action",
        graph: Optional[Graph] = None,
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.from_screen = from_screen
        self.to_screen = to_screen
        self.trigger = trigger or name
        self.nav_type = nav_type


class ContentType(UxComponent):
    _semantic_type_name = "ContentType"

    def __init__(
        self, name: str, sequential_order: int, hierarchy: str = "", graph: Optional[Graph] = None
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.hierarchy = hierarchy
        self.key_actions: List[str] = []


class NavComponent(UxComponent):
    _semantic_type_name = "NavComponent"

    def __init__(
        self, name: str, sequential_order: int, ux_type: str = "", graph: Optional[Graph] = None
    ) -> None:
        super().__init__(name, sequential_order, graph)
        self.ux_type = ux_type
        self.destinations: List[Screen] = []


class UxContext(UxNode):
    """Optional notes - invariants / thinking not on screens."""

    _semantic_type_name = "UxContext"

    def __init__(self, name: str = "context", sequential_order: int = 0, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.notes: List[str] = []
        self.invariants: List[str] = []
