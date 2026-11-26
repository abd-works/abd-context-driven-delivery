"""Live check of the story map's screen cells: test-area/pml-web's story map, read on one graph with its UX map, rendered
to draw.io and to a whiteboard into the session folder, unpublished.

test-area/pml-web holds no design canvas, so the workspace is a throwaway copy of it beside the canvas screens of
pml-web's latest version (``ux/design-canvas/version-7/project/screens``), copied read only. Screen cells should appear
under each story a screen shows whose prototype file the copy holds, and nowhere else.

usage: screens_check.py <workspace folder> <pml-web folder>"""
import os
import re
import shutil
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent

import cdd_guidance.practices  # registers the practices a graph reads
from harness.graph.graph import Graph
from cdd_guidance.practices.stories.model.story_map import Epic, StoryMap
from harness.guidance.practice_formats import Written
from harness.whiteboard.whiteboard import Whiteboard
from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryMap
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryMap

workspace, pml_web = Path(sys.argv[1]), Path(sys.argv[2])
if workspace.exists():
    # git marks its objects read-only, which Windows will not delete until the mark is taken off.
    shutil.rmtree(workspace, onexc=lambda remove, path, _: (os.chmod(path, stat.S_IWRITE), remove(path)))
shutil.copytree(ROOT / "test-area" / "pml-web", workspace)
screens = "ux/design-canvas/version-7/project/screens"
shutil.copytree(pml_web / screens, workspace / screens, ignore=shutil.ignore_patterns("explorer.dc.html", "flow.dc.html"))
subprocess.run(["git", "init", "-q", "-b", "main", str(workspace)], check=True)
subprocess.run(["git", "-C", str(workspace), "remote", "add", "origin", "https://github.com/org/pml-web.git"], check=True)

graph = Graph()
graph.load_files(str(workspace), ["stories", "ux"], ["tests", "ux"])
# The graph holds the map's epics under its practice; a map made to hold its top epics stands in for the one read.
story_map = StoryMap()
for epic in graph.practices.named("stories").reading.in_graph.nodes("Epic"):
    if not isinstance(epic.parent, Epic):
        story_map.epics.append(epic)
folder = workspace / "tests" / ".context"
stories = list(story_map.descendants.stories())
held = {path.name for path in (workspace / screens).iterdir()}
expected = sorted((story.name, screen.name) for story in stories for screen in story.screens
                  if Path(str(getattr(screen, "prototype", ""))).name in held)

drawio = DrawIOStoryMap().render(story_map, Written(folder=folder))
(OUT / "pml-web-story-map.drawio").write_text(drawio, encoding="utf-8")
tree = ET.fromstring(drawio)
cells = [cell for cell in tree.iter("mxCell") if (cell.get("style") or "").startswith("screen;")]
holders = {id(cell): holder for holder in tree.iter("UserObject") for cell in holder}
links = [holders[id(cell)].get("link") for cell in cells]
broken = [link for link in links if not (folder / link).is_file()]
drawn = sorted((cell_id.split("/screen/")[0], holders[id(cell)].get("label")) for cell, cell_id in ((c, holders[id(c)].get("id")) for c in cells))
print(f"stories: {len(stories)}, shown on a screen: {sum(1 for story in stories if story.screens)}, screens with a prototype file: {len(expected)}")
print(f"draw.io: {len(cells)} screen cells, broken links: {broken or 'none'}, e.g. {links[:2]}")
print(f"draw.io stories read back: {len(DrawIOStoryMap().parse(drawio).descendants.stories())} (map has {len(stories)})")

board = WhiteboardStoryMap().render(story_map, Written(folder=folder))
(OUT / "pml-web-story-map.whiteboard").write_text(board, encoding="utf-8")
cards = [element.text for element in Whiteboard.from_text(board).elements if element.role == "screen"]
paths = [re.search(r"/blob/main/([^)]+)\)", card).group(1) for card in cards]
print(f"whiteboard: {len(cards)} screen cards, broken: {[p for p in paths if not (workspace / p).is_file()] or 'none'}, e.g. {cards[:1]}")
print(f"whiteboard stories read back: {len(WhiteboardStoryMap().parse(board).descendants.stories())}")
print(f"every expected screen drawn once: {len(cells) == len(expected) == len(cards)}")
