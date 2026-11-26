"""A story map on a graph that also reads a UX map, so its stories are shown on screens, written in a folder.

The folder holds ``story-map.md`` and the UX map ``ux/ux.json`` with its design canvas at ``ux/design-canvas/version-1``.
Select Sim is shown on three screens: Select Sim Screen, whose prototype the canvas holds; Pick Plan, whose prototype
it does not; and Far Screen, whose prototype is a file outside the folder. Activate Sim is shown on none.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from harness.graph.graph import Graph, Source
from harness.graph.location import Location

from cdd_guidance.practices.stories.model.story_map import Epic, Story, StoryMap
from cdd_guidance.practices.ux.model.nodes import Screen

SHOWN_MAP = """# (E) Onboard A Customer
## (E) Get Sim
### (S) Customer --> Select Sim
### (S) Customer --> Activate Sim
"""

UX_MAP = "ux/ux.json"
PORTED_SCREEN = "ux/design-canvas/version-1/project/screens/select-sim.dc.html"
# A file beside the folder, which Far Screen's prototype leads to from the canvas's project folder, five folders down.
OUTSIDE_SCREEN = "elsewhere/far.dc.html"


def shown_folder(root: Path, files: Dict[str, str] | None = None) -> Path:
    """root holding the story map, the UX map, the one ported screen, and files; root's parent holding the screen file
    outside it."""
    (root.parent / OUTSIDE_SCREEN).parent.mkdir(parents=True, exist_ok=True)
    (root.parent / OUTSIDE_SCREEN).write_text("<div></div>\n", encoding="utf-8")
    for relative, text in {"story-map.md": SHOWN_MAP, UX_MAP: "{}\n", PORTED_SCREEN: "<div></div>\n", **(files or {})}.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    return root


def shown_story_map(root: Path) -> StoryMap:
    """The map of SHOWN_MAP on a graph whose UX map, read from root's ``ux/ux.json``, shows Select Sim on three screens."""
    graph = Graph()
    story_map = StoryMap(graph=graph)
    onboard, get_sim = Epic("Onboard A Customer", 1), Epic("Get Sim", 1)
    story_map.epics.append(onboard)
    onboard.epics.append(get_sim)
    select, activate = Story("Select Sim", 1), Story("Activate Sim", 2)
    for story in (select, activate):
        story.actors = ["Customer"]
        get_sim.stories.append(story)
    for order, (name, prototype) in enumerate((("Select Sim Screen", "screens/select-sim.dc.html"), ("Pick Plan", "screens/pick-plan.dc.html"),
                                                ("Far Screen", f"../../../../../{OUTSIDE_SCREEN}"))):
        screen = Screen(name, order, graph=graph)
        screen.prototype = prototype
        screen.source = Source.from_root(str(root), Location(UX_MAP, 1, 1))
        screen.show_story(select)
    return story_map
