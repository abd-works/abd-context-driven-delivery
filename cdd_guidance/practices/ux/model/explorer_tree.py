"""ExplorerTree - the story explorer's tree of a UX map, which the mockup page carries for its JavaScript to draw."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.stories.model.graph_reading import StoryTree

    from .nodes import Screen

# One entry of the explorer's tree as its JavaScript reads it: a screen, a story, a scenario, or a step, by its kind.
type ExplorerEntry = dict


class ExplorerScreen:
    """One screen as the story explorer lists it: by the slug the mockup page marks it with, holding each story it
    shows with that story's scenarios and their steps, read from the story map when the story is on the map's graph.
    Each is read from the story map's tree as the graph holds it (story_tree), so a graph opened from its save, whose
    Stories nodes are plain nodes, gives the tree a fresh build gives."""

    def __init__(self, screen: "Screen", story_tree: Optional["StoryTree"]) -> None:
        self.name = screen.slug or screen.name
        self.story_tree = story_tree
        # The words the screen's steps mark as the domain's own: the terms the model gives the screen.
        self.domain_terms = list(screen.domain_terms)
        self.stories: List[tuple[Optional["Node"], dict]] = [
            (link.node, self._story_entry(link.key, link.node)) for link in screen.story_links
        ]

    @property
    def key(self) -> str:
        return f"screen:{self.name}"

    def entry(self) -> dict:
        """The screen listed on its own, with every story it shows."""
        return {"kind": "screen", "name": self.name, "key": self.key, "children": [entry for _story, entry in self.stories]}

    def placed_entry(self, order: Dict[int, int], place: str) -> Optional[tuple[int, dict]]:
        """The screen placed under an epic or a sub-epic (place, `Epic/Sub-epic`), holding only the stories it shows
        there in story-map order (order, by story), ranked by the first of them; none when it shows none there."""
        shown = sorted(((order[id(story)], entry) for story, entry in self.stories if id(story) in order), key=lambda item: item[0])
        if not shown:
            return None
        entry = {"kind": "screen", "name": self.name, "key": f"screen:{place}/{self.name}", "children": [item[1] for item in shown]}
        return shown[0][0], entry

    def _story_entry(self, name: str, story: Optional["Node"]) -> dict:
        key = f"story:{self.name}/{name}"
        scenarios = [self._scenario_entry(name, index, scenario) for index, scenario in enumerate(self.story_tree.scenarios(story))] if story is not None else []
        return {"kind": "story", "name": name, "screenName": self.name, "key": key, "children": scenarios}

    def _scenario_entry(self, story_name: str, index: int, scenario: "Node") -> dict:
        key = f"scenario:{self.name}/{story_name}/{scenario.name}"
        scenario_entry = {"kind": "scenario", "name": scenario.name, "screenName": self.name, "key": key, "storyName": story_name, "scenarioIndex": index}
        steps = [self._step_entry(scenario_entry, step) for step in self.story_tree.steps(scenario)]
        return {**scenario_entry, "children": steps}

    def _step_entry(self, scenario_entry: ExplorerEntry, step: "Node") -> ExplorerEntry:
        """A step as the explorer lists it under its scenario (scenario_entry): it carries the scenario's story, index,
        and key, so the explorer plays the scenario from any of its steps."""
        return {
            "kind": "step",
            "screenName": self.name,
            "stepKind": step.get_fact("phase") or "",
            "label": step.get_fact("text") or "",
            "domainTerms": self.domain_terms,
            "storyName": scenario_entry["storyName"],
            "scenarioIndex": scenario_entry["scenarioIndex"],
            "scenarioKey": scenario_entry["key"],
        }


class ExplorerTree:
    """The story explorer's tree of a map: each epic of the story map above the stories the screens show, in the order
    the screens first show it, then its sub-epics at any depth that hold a shown story, then the screens under each by
    the stories they show there, ranked by the first of those in story-map order; a screen whose stories sit on the
    epic itself hangs on the epic. Each screen then holds its stories, their scenarios, and their steps. A screen can
    sit under several epics; one that shows no story on the story map is left off. With no story map on the map's
    graph, the screens are listed flat. The tree names, for each screen, the keys the explorer opens to show it: those
    of the first place it sits."""

    def __init__(self, screens: List["Screen"]) -> None:
        shown = [link.node for screen in screens for link in screen.story_links if link.node is not None]
        self.story_tree: Optional["StoryTree"] = shown[0].practice.reading.story_tree if shown else None
        self.screens = [ExplorerScreen(screen, self.story_tree) for screen in screens]
        self.shown_stories: List["Node"] = [story for screen in self.screens for story, _entry in screen.stories if story is not None]
        self.screen_keys: Dict[str, List[str]] = {}
        self.nodes = self._epic_entries() or self._flat_entries()

    def as_json(self) -> dict:
        """The tree as the mockup page carries it."""
        return {"nodes": self.nodes, "screenKeys": self.screen_keys}

    def _flat_entries(self) -> List[dict]:
        self.screen_keys = {screen.name: [screen.key] for screen in self.screens}
        return [screen.entry() for screen in self.screens]

    def _epic_entries(self) -> List[dict]:
        epics: List["Node"] = []
        for story in self.shown_stories:
            epic = self.story_tree.epic_of(story)
            if epic is not None and epic not in epics:
                epics.append(epic)
        return [entry for entry in (self._epic_entry(epic) for epic in epics) if entry is not None]

    def _epic_entry(self, epic: "Node") -> Optional[dict]:
        epic_key = f"epic:{epic.name}"
        children: List[dict] = []
        pending = list(self.story_tree.sub_epics(epic))
        while pending:
            sub_epic = pending.pop(0)
            sub_key = f"subepic:{epic.name}/{sub_epic.name}"
            placed = self._placed(self.story_tree.stories_under(sub_epic), f"{epic.name}/{sub_epic.name}", [epic_key, sub_key])
            if placed:
                children.append({"kind": "subepic", "name": sub_epic.name, "key": sub_key, "children": placed})
            pending[:0] = self.story_tree.sub_epics(sub_epic)
        children.extend(self._placed(self.story_tree.stories_under(epic), f"{epic.name}/", [epic_key]))
        return {"kind": "epic", "name": epic.name, "key": epic_key, "children": children} if children else None

    def _placed(self, stories: List["Node"], place: str, opening: List[str]) -> List[dict]:
        """The screens that show any of stories, each holding those it shows, ranked by the first in story-map order;
        each placed screen's keys are recorded the first time it is placed."""
        order = {id(story): index for index, story in enumerate(item for item in stories if item in self.shown_stories)}
        ranked = [found for found in (screen.placed_entry(order, place) for screen in self.screens) if found is not None]
        ranked.sort(key=lambda item: item[0])
        for _rank, entry in ranked:
            self.screen_keys.setdefault(entry["name"], [*opening, entry["key"]])
        return [entry for _rank, entry in ranked]
