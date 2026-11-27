"""ShownPlaces. Where on the UX map each story, scenario, step and example is shown, and what each screen shows, read
through the edges the graph already records between Stories and UX: a screen or a control ``shows``,
``showsScenarios`` and ``showsSteps`` what it serves and each of those records ``shownOn`` it back; a Story Demo control
runs the steps its ``storySteps`` name and each of those records ``runBy`` it back.

A step shows on its own screen or control when the map names one for it, else on its scenario's, else on its story's,
as the schema says a scenario with no screen of its own shows its story's screen; an example shows where its scenario
does. A control is placed on the screen whose region holds it, with the interactions it starts."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from cdd_guidance.practices.stories.model.story_tree import EXAMPLE_TYPE, StoryTree

if TYPE_CHECKING:
    from harness.graph.graph import Graph, Node

SHOWN_ON = "shownOn"
"""The edge a story, scenario or step records to each screen or control it is shown on."""
RUN_BY = "runBy"
"""The edge a step records to each Story Demo control that runs it, the back-edge of the control's ``storySteps``."""
_SHOWN_EDGES = ("shows", "showsScenarios", "showsSteps", "storySteps")
_CONTROL_TYPES = ("Control", "StoryDemoControl")


class ShownPlace:
    """One place on the UX map a Stories node is shown: a screen, the control on it when the map names one, the
    interactions that control starts, and the Stories node whose edge leads there: the node itself, or the scenario
    or story it falls back to."""

    def __init__(self, screen: "Node", control: Optional["Node"], interactions: List["Node"], through: "Node") -> None:
        self.screen = screen
        self.control = control
        self.interactions = interactions
        self.through = through

    @property
    def described(self) -> str:
        """The place in words: the screen, its file, its prototype, the control and its interactions."""
        file = self.screen.source.file if self.screen.source is not None else ""
        prototype = _said(self.screen, "prototype")
        parts = [f"screen {self.screen.name}" + (f" ({file})" if file else "") + (f", drawn by {prototype}" if prototype else "")]
        if self.control is not None:
            parts.append(f"control {self.control.name}")
        if self.interactions:
            parts.append("interactions " + ", ".join(interaction.name for interaction in self.interactions))
        return "; ".join(parts)


class ShownPlaces:
    """The traversal between Stories and UX on one graph, both ways: the places a Stories node is shown (``of``), and the
    stories, scenarios and steps a screen shows (``shown_on``)."""

    def __init__(self, graph: "Graph") -> None:
        self._graph = graph
        self._edges = graph.edges
        self._tree = StoryTree.of_graph(graph)

    def of(self, node: "Node") -> List[ShownPlace]:
        """The places node is shown: its own, else its scenario's, else its story's; an example's are its scenario's."""
        if self._tree is None:
            return []
        for through in self._falling_back_from(node):
            own = self._own_places(through)
            if own:
                return own
        return []

    def shown_on(self, screen: "Node") -> List["Node"]:
        """Every story, scenario and step screen shows: what it and each control on it serve and run, and every scenario
        and step of the stories and scenarios among them, in the order the map gives them."""
        found: List["Node"] = []
        for server in [screen, *self._controls_on(screen)]:
            for kind in _SHOWN_EDGES:
                for edge in self._edges.from_parent(kind, server):
                    self._take(found, edge.child)
        return found

    def _take(self, found: List["Node"], node: "Node") -> None:
        if any(node is held for held in found):
            return
        found.append(node)
        if self._tree is None:
            return
        if node.type == "Story":
            for scenario in self._tree.scenarios(node):
                self._take(found, scenario)
        elif node.type in ("Scenario", "Background"):
            for step in self._steps_with_ands(node):
                self._take(found, step)

    def _steps_with_ands(self, scenario: "Node") -> List["Node"]:
        steps: List["Node"] = []
        for step in self._tree.steps(scenario):
            steps.append(step)
            steps.extend(edge.child for edge in self._edges.from_parent("ands", step))
        return steps

    def _falling_back_from(self, node: "Node") -> List["Node"]:
        """node, then the scenario and the story it sits in, the nodes whose places it shows when it has none of its own."""
        chain = [node]
        scenario = self._tree.scenario_of(node) if node.type != EXAMPLE_TYPE else self._edges.direct_parent(node)
        if scenario is not None and scenario.type in ("Scenario", "Background"):
            chain.append(scenario)
        story = self._tree.story_of(node)
        if story is not None:
            chain.append(story)
        return chain

    def _own_places(self, node: "Node") -> List[ShownPlace]:
        places: List[ShownPlace] = []
        for kind in (SHOWN_ON, RUN_BY):
            for edge in self._edges.from_parent(kind, node):
                place = self._place_of(edge.child, node)
                if place is not None:
                    places.append(place)
        return places

    def _place_of(self, shown_on: "Node", through: "Node") -> Optional[ShownPlace]:
        """The place a ``shownOn`` or ``runBy`` edge leads to: a screen itself, or a control on its screen."""
        if shown_on.type == "Screen":
            return ShownPlace(shown_on, None, [], through)
        if shown_on.type not in _CONTROL_TYPES:
            return None
        screen = self._screen_of(shown_on)
        return ShownPlace(screen, shown_on, self._interactions_of(shown_on), through) if screen is not None else None

    def _screen_of(self, control: "Node") -> Optional["Node"]:
        above = self._edges.direct_parent(control)
        while above is not None and above.type != "Screen":
            above = self._edges.direct_parent(above)
        return above

    def _interactions_of(self, control: "Node") -> List["Node"]:
        held = self._graph.practices.part_of(control.practice).nodes("Interaction") if control.practice is not None else []
        return [interaction for interaction in held if self._edges.direct_parent(interaction) is control]

    def _controls_on(self, screen: "Node") -> List["Node"]:
        if screen.practice is None:
            return []
        part = self._graph.practices.part_of(screen.practice)
        return [control for kind in _CONTROL_TYPES for control in part.nodes(kind) if self._screen_of(control) is screen]


def _said(node: "Node", name: str) -> str:
    """What node says for name: the model object's attribute, else the fact a node read back from a save keeps."""
    value = getattr(node, name, None)
    return str(value or node.get_fact(name) or "")
