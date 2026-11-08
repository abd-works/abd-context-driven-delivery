"""Concrete UX node types: Screen, Region, Control, and peers.

Every node is built on, or moved onto, its map's graph: the lists that hold a node's children record the graph edge
when a child is appended. Links from one screen to another hold the Screen itself, so renaming a screen keeps them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Mapping, Optional

from harness.annotations.name import Name
from harness.graph.model_node import ModelChildren
from harness.graph.graph import Graph, Node

from .story_link import StoryLink
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
        self.interactions = ModelChildren(self, "interactions")

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
        self.controls = ModelChildren(self, "controls")

    def append_control(self, control: Control) -> None:
        self.controls.append(control)
        self._renumber(self.controls)


class Screen(UxNode):
    """One screen of the map.

    It shows stories, scenarios, and steps through one StoryLink each: the Stories node once it is on the screen's
    graph, else the key the formats store. ``shows``, ``shows_scenarios``, and ``shows_steps`` are the nodes the graph
    records as the screen's edges of those names, and each of those nodes records ``shownOn`` this screen.
    """

    _semantic_type_name = "Screen"

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
        self._story_links: List[StoryLink] = []
        self.domain_terms: List[str] = []
        self.domain_concepts: List[str] = []
        self.image = ""
        self.prototype = ""
        self.regions = ModelChildren(self, "regions")

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

    def show_story(self, story: Node | str) -> None:
        """A story this screen shows: the Story, or its name."""
        self._show("Story", story)

    def show_scenario(self, scenario: Node | str) -> None:
        """A scenario this screen shows: the Scenario, or its key ``Story › Scenario``."""
        self._show("Scenario", scenario)

    def show_step(self, step: Node | str) -> None:
        """A step this screen shows: the Step, or its key ``Story › Scenario › Step``."""
        self._show("Step", step)

    @property
    def shows(self) -> List[Node]:
        """The stories on this screen's graph that it shows."""
        return self._shown_nodes("Story")

    @property
    def shows_scenarios(self) -> List[Node]:
        return self._shown_nodes("Scenario")

    @property
    def shows_steps(self) -> List[Node]:
        return self._shown_nodes("Step")

    @property
    def story_keys(self) -> List[str]:
        """The stories this screen shows, as the formats write them."""
        return self._keys("Story")

    @property
    def scenario_keys(self) -> List[str]:
        return self._keys("Scenario")

    @property
    def step_keys(self) -> List[str]:
        return self._keys("Step")

    def lists(self, node: Node) -> bool:
        """True when this screen shows that story, scenario, or step, or one with its key drawn on another graph."""
        return any(link.names(node) for link in self._story_links)

    def show_what(self, other: "Screen") -> None:
        """Show the stories, scenarios, and steps other shows: each Stories node other finds on its own graph, else
        the key other holds for it."""
        for link in other._story_links:
            resolved = link.resolved_on(other.graph) if other.practice is not None else None
            self._show(link.kind, resolved or link.key)

    def attach_domain_term(self, term: str) -> None:
        if term and term not in self.domain_terms:
            self.domain_terms.append(term)

    def _show(self, kind: str, item: Node | str) -> None:
        link = StoryLink.from_item(kind, item)
        if not link.key or link.key in self._keys(kind):
            return
        self._story_links.append(link)
        self._sync_schema_edges()

    def _shown_nodes(self, kind: str) -> List[Node]:
        """The Stories nodes this screen's links of kind name on its graph. While no practice holds the screen, the
        nodes its links already hold, as a copy of a screen keeps the nodes its source found."""
        links = [link for link in self._story_links if link.kind == kind]
        if self.practice is None:
            return [link.node for link in links if link.node is not None]
        found = (link.resolved_on(self.graph) for link in links)
        return [node for node in found if node is not None]

    def _keys(self, kind: str) -> List[str]:
        return [link.key for link in self._story_links if link.kind == kind]


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
