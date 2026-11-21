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
    def from_value(cls, step: "StoryStep | Mapping[str, Any]") -> "StoryStep":
        """A step from a file's ``{kind, label}`` object, or the step itself."""
        if isinstance(step, StoryStep):
            return step
        return cls(str(step.get("kind", "") or ""), str(step.get("label", "") or ""))

    @classmethod
    def from_values(cls, steps: Iterable["StoryStep | Mapping[str, Any]"] | None) -> List["StoryStep"]:
        """Each step a file lists, in its order; none for a file that lists none."""
        return [cls.from_value(step) for step in steps or ()]

    def as_dict(self) -> dict:
        return {"kind": self.kind, "label": self.label}


class Interaction(UxNode):
    """What a control does when it is triggered: the trigger, its effect, and the screen it goes to. Each is set on
    the interaction once it is made."""

    _semantic_type_name = "Interaction"
    graph_facts = ("trigger", "effect")

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self._trigger = ""
        self.effect = ""
        self.destination: Optional["Screen"] = None

    @property
    def trigger(self) -> str:
        """What sets it off, such as a click; its name while it names none."""
        return self._trigger or self.name

    @trigger.setter
    def trigger(self, trigger: str) -> None:
        self._trigger = trigger

    @property
    def destination_name(self) -> str:
        """The name of the screen it goes to; blank while it goes to none."""
        return self.destination.name if self.destination is not None else ""


class ServesStories(UxNode):
    """A node of the map that serves stories: a screen, or a control on it.

    It serves stories, scenarios, and steps through one StoryLink each: the Stories node once it is on the node's
    graph, else what the formats store, the key and the link target the association was written with. ``shows``,
    ``shows_scenarios``, and ``shows_steps`` are the nodes the graph records as its edges of those names, and each of
    those nodes records ``shownOn`` this node.
    """

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self._story_links: List[StoryLink] = []

    def show_story(self, story: Node | str) -> None:
        """A story this node serves: the Story, or its name."""
        self._show("Story", story)

    def show_scenario(self, scenario: Node | str) -> None:
        """A scenario this node serves: the Scenario, or its key ``Story › Scenario``."""
        self._show("Scenario", scenario)

    def show_step(self, step: Node | str) -> None:
        """A step this node serves: the Step, or its key ``Story › Scenario › Step``."""
        self._show("Step", step)

    @property
    def shows(self) -> List[Node]:
        """The stories on this node's graph that it serves."""
        return self._shown_nodes("Story")

    @property
    def shows_scenarios(self) -> List[Node]:
        return self._shown_nodes("Scenario")

    @property
    def shows_steps(self) -> List[Node]:
        return self._shown_nodes("Step")

    @property
    def story_keys(self) -> List[str]:
        """The stories this node serves, as the formats write them: each a markdown link to the file and heading the story
        is written at when the link names one, ``[Browse Books](story-map.md#story-browse-books)``, else its name."""
        return self._keys("Story")

    @property
    def scenario_keys(self) -> List[str]:
        return self._keys("Scenario")

    @property
    def step_keys(self) -> List[str]:
        return self._keys("Step")

    def lists(self, node: Node) -> bool:
        """True when this node serves that story, scenario, or step, or one with its key drawn on another graph."""
        return any(link.names(node) for link in self._story_links)

    def show_what(self, other: "ServesStories") -> None:
        """Serve the stories, scenarios, and steps other serves: each Stories node other finds on its own graph, else
        the key and the link target other holds for it."""
        for link in other._story_links:
            resolved = link.resolved_on(other.graph) if other.practice is not None else None
            self._show(link.kind, resolved or link.written)

    def _show(self, kind: str, shown: Node | str) -> None:
        link = StoryLink.from_shown(kind, shown)
        if not link.key or any(held.key == link.key and held.target == link.target for held in self.links_of(kind)):
            return
        self._story_links.append(link)
        self._sync_schema_edges()

    @property
    def story_links(self) -> List[StoryLink]:
        """The stories this node serves, in the order it serves them: each link holds its Story once the node's
        graph has it, else only the name the formats write."""
        return self._links("Story")

    def _shown_nodes(self, kind: str) -> List[Node]:
        """The Stories nodes this node's links of kind name on its graph."""
        return [link.node for link in self._links(kind) if link.node is not None]

    def _links(self, kind: str) -> List[StoryLink]:
        """This node's links of kind, each holding the node it names on the node's graph. While no practice holds
        the node, each holds the node it already held, as a copy keeps the nodes its source found."""
        links = self.links_of(kind)
        if self.practice is not None:
            for link in links:
                link.resolved_on(self.graph)
        return links

    def links_of(self, kind: str) -> List[StoryLink]:
        """The stories, scenarios, or steps (kind) this node serves, in the order it serves them, as it holds them."""
        return [link for link in self._story_links if link.kind == kind]

    def _keys(self, kind: str) -> List[str]:
        return [link.written for link in self.links_of(kind)]


class Control(ServesStories):
    """A control on a region: its type, the label it shows, the field it shows the value of, and the stories,
    scenarios, and steps it serves. Each is set on the control once it is made."""

    _semantic_type_name = "Control"
    graph_facts = ("control_type", "label", "bound_field", "states", "story_keys", "scenario_keys", "step_keys")

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.control_type = ""
        self._label = ""
        self.bound_field = ""
        self.states: List[str] = []
        self.interactions = ModelChildren(self, "interactions")

    @property
    def label(self) -> str:
        """What the control shows; its name while it names no label."""
        return self._label or self.name

    @label.setter
    def label(self, label: str) -> None:
        self._label = label

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
    graph_facts = (*Control.graph_facts, "story_step_labels", "set_input", "item_value", "item_label")

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.story_steps: List[StoryStep] = []
        self.set_input = ""
        self.item_story_steps: List[StoryStep] = []
        self.item_value = ""
        self.item_label = ""

    @property
    def story_step_labels(self) -> List[str]:
        """The text of each story step this control runs, as Stories wrote it."""
        return [step.label for step in self.story_steps]

    def take_story_fields(self, source: "StoryDemoControl") -> None:
        """Run the steps source runs, fill the input it fills, and show its items the way it does."""
        self.story_steps = list(source.story_steps)
        self.set_input = source.set_input
        self.item_story_steps = list(source.item_story_steps)
        self.item_value = source.item_value
        self.item_label = source.item_label


class Region(UxNode):
    _semantic_type_name = "Region"
    graph_facts = ("area",)

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.area = ""
        self.controls = ModelChildren(self, "controls")

    def append_control(self, control: Control) -> None:
        self.controls.append(control)
        self._renumber(self.controls)


class Screen(ServesStories):
    """One screen of the map, with the stories, scenarios, and steps it serves."""

    _semantic_type_name = "Screen"
    graph_facts = ("slug", "layout", "description", "story_keys", "scenario_keys", "step_keys", "domain_terms")

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        """A screen called name; its slug, layout, description, and the screen it is the chrome of are set on it once
        it is made."""
        super().__init__(name, sequential_order, graph)
        self._slug = ""
        self.layout = ""
        self.description = ""
        self.chrome_of: Optional["Screen"] = None
        self.inactive_tabs: List[str] = []
        self.domain_terms: List[str] = []
        self.domain_concepts: List[str] = []
        self.image = ""
        self.prototype = ""
        self.regions = ModelChildren(self, "regions")

    @property
    def slug(self) -> str:
        """The screen's name as a file or a link spells it; from its name while it is given none."""
        return self._slug or Name(self.name).title_slug

    @slug.setter
    def slug(self, slug: str) -> None:
        self._slug = slug

    @property
    def chrome_of_name(self) -> str:
        """The name of the screen it is the chrome of; blank while it is the chrome of none."""
        return self.chrome_of.name if self.chrome_of is not None else ""

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

    def attach_domain_term(self, term: str) -> None:
        if term and term not in self.domain_terms:
            self.domain_terms.append(term)


class UxComponent(UxNode):
    """A structural peer of the screens on the map: a transition, a content type, or a nav component."""

    _semantic_type_name = "UxComponent"


class Transition(UxComponent):
    _semantic_type_name = "Transition"
    graph_facts = ("trigger", "nav_type")

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        """A transition called name; the screens it joins, its trigger, and its kind of navigation are set on it once
        it is made (``joining``)."""
        super().__init__(name, sequential_order, graph)
        self.from_screen: Optional[Screen] = None
        self.to_screen: Optional[Screen] = None
        self._trigger = ""
        self.nav_type = "action"

    def joining(self, from_screen: Optional[Screen], to_screen: Optional[Screen]) -> "Transition":
        """This transition going from from_screen to to_screen; answers itself."""
        self.from_screen = from_screen
        self.to_screen = to_screen
        return self

    @property
    def from_name(self) -> str:
        """The name of the screen it leaves; blank while it leaves none."""
        return self.from_screen.name if self.from_screen is not None else ""

    @property
    def to_name(self) -> str:
        """The name of the screen it goes to; blank while it goes to none."""
        return self.to_screen.name if self.to_screen is not None else ""

    @property
    def trigger(self) -> str:
        """What sets it off; its name while it names none."""
        return self._trigger or self.name

    @trigger.setter
    def trigger(self, trigger: str) -> None:
        self._trigger = trigger


class ContentType(UxComponent):
    _semantic_type_name = "ContentType"
    graph_facts = ("hierarchy", "key_actions")

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.hierarchy = ""
        self.key_actions: List[str] = []


class NavComponent(UxComponent):
    _semantic_type_name = "NavComponent"
    graph_facts = ("ux_type",)

    def __init__(self, name: str, sequential_order: int, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.ux_type = ""
        self.destinations: List[Screen] = []


class UxContext(UxNode):
    """Optional notes - invariants / thinking not on screens."""

    _semantic_type_name = "UxContext"
    graph_facts = ("notes", "invariants")

    def __init__(self, name: str = "context", sequential_order: int = 0, graph: Optional[Graph] = None) -> None:
        super().__init__(name, sequential_order, graph)
        self.notes: List[str] = []
        self.invariants: List[str] = []
