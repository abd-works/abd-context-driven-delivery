"""Claude Design story map: a canvas with the story map on one page and the screens on another.

The story map page holds one artboard: epic and sub-epic bars, actors, stories, and under each
story the thumbnail of its main screen. The screens page holds the story explorer and the
prototype screens. The canvas itself (pages, boards, canvas.json) is ``harness.design_canvas``;
render returns its files as JSON: ``{"project/<path>": "<file text>"}``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote, urlencode

from harness.design_canvas.canvas import DesignCanvas, artboard, box, camel, escape, stem, thumbnail
from harness.design_canvas.look import BACKGROUND, FONTS, LOOK
from harness.graph.schema_edges import scenario_key, step_key

from cdd_guidance.practices.ux.model.claude_design.nodes import ClaudeDesignUxMap

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel

_EXPLORER_TEMPLATE = Path(__file__).with_name("explorer.dc.html")
_SHOWN_ON = "shownOn"


class ClaudeDesignEpic(DiagramEpic):
    """An epic or sub-epic: its bars over its stories' columns, at the drawio's own scale."""

    bar_height = 60
    sub_bar_height = 70
    bar_gap = 20

    def leaf_epics(self) -> List["ClaudeDesignEpic"]:
        """The epics whose stories sit in columns: sub-epics, or this epic when it has none."""
        if not self.epics:
            return [self]
        found: List[ClaudeDesignEpic] = []
        for child in self.epics:
            found.extend(child.leaf_epics())
        return found

    def top_epic(self) -> "ClaudeDesignEpic":
        node = self
        while isinstance(node.parent, Epic):
            node = node.parent
        return node

    def column_width(self) -> int:
        count = max(len(self.stories), 1)
        return count * ClaudeDesignStory.width_px + (count - 1) * ClaudeDesignStory.gap_px

    def header_parts(self, left: int) -> List[str]:
        """The sub-epic bar and each story's actor and card, from *left* on the story map. The epic bar spans its sub-epics; the map draws it."""
        width = self.column_width()
        top = self.top_epic()
        parts: List[str] = []
        if self is not top:
            parts.append(box(left, self.bar_height + self.bar_gap, width, self.sub_bar_height, LOOK["sub_epic"], self.name))
        for index, story in enumerate(self.stories):
            parts.extend(story.header_cells(left + index * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px), self.story_top()))
        return parts

    @classmethod
    def story_top(cls) -> int:
        return cls.bar_height + cls.bar_gap + cls.sub_bar_height + cls.bar_gap

    @classmethod
    def header_height(cls) -> int:
        return cls.story_top() + ClaudeDesignStory.actor_px + ClaudeDesignStory.actor_gap_px + ClaudeDesignStory.card_px


class ClaudeDesignStory(DiagramStory):
    """A story column: its actor and card in the header, then one thumbnail per screen its steps show."""

    width_px = 160
    gap_px = 20
    actor_px = 40
    actor_gap_px = 10
    card_px = 70
    thumb_px = 112
    thumb_gap_px = 16

    def header_cells(self, left: int, top: int) -> List[str]:
        actor = (self.actors or ["Customer"])[0]
        person = ('<svg width="10" height="14" viewBox="0 0 14 20" aria-hidden="true" style="fill: none; stroke: #9B9BA8; '
                  'stroke-width: 1.5"><circle cx="7" cy="3.5" r="2.5"></circle><path d="M7 6v7M1 9h12M7 13l-5 6M7 13l5 6"></path></svg>')
        return [
            box(left, top, self.width_px, self.actor_px, LOOK["actor"], actor, icon=person),
            box(left, top + self.actor_px + self.actor_gap_px, self.width_px, self.card_px, LOOK["story"], self.name),
        ]

    def shown_screens(self, screens: List) -> List[tuple]:
        """Each (scenario, step, screen) this story's steps are shown on, in scenario order, once per screen image."""
        seen: set = set()
        found: List[tuple] = []
        for scenario in [*self.backgrounds, *self.scenarios]:
            for step in _steps_of(scenario):
                for screen in shown_on(step, screens):
                    marker = screen.image or screen.name
                    if marker in seen:
                        continue
                    seen.add(marker)
                    found.append((scenario, step, screen))
        for screen in screens:
            marker = screen.image or screen.name
            if marker not in seen and self.name in list(getattr(screen, "story_names", []) or []):
                seen.add(marker)
                found.append((None, None, screen))
        return found


class ClaudeDesignStoryModel(DiagramStoryModel):
    """Claude Design canvas I/O. IS the format-typed tree root; render writes the canvas files."""

    epic_type = ClaudeDesignEpic
    story_type = ClaudeDesignStory
    story_map_page = "story-map"
    screens_page = ClaudeDesignUxMap.page
    screens_folder = ClaudeDesignUxMap.folder
    sub_epic_gap = 40
    thumbs_gap = 24
    margin = 24
    screens_per_story = 1
    blank_image_bytes = 10000
    sources: Dict[str, str] = {}

    def render(
        self,
        canonical: Optional[StoryModel] = None,
        previous: Optional[str] = None,
        workspace: Optional[str] = None,
        screens=None,
        sources: Optional[Dict[str, str]] = None,
    ) -> str:
        """The canvas files as JSON. *screens* is a UxMap (or its screens); with only a *workspace*
        (the canvas root), the UX map beside it — ``ux.json`` in the folder that holds the canvas — supplies them.
        *sources* maps a story (``Story``) or scenario (``Story › Scenario``) to its ``path:line`` in the story code:
        the explorer offers to copy an "open in the file viewer" request for it."""
        source = canonical if canonical is not None else self
        drawn = source if isinstance(source, ClaudeDesignStoryModel) else type(self)(source)
        drawn.workspace = Path(workspace) if workspace else None
        drawn.screens = drawn._screens(screens)
        drawn.sources = dict(sources or {})
        return json.dumps(drawn.files(), indent=1, ensure_ascii=False)

    def parse(self, text: str) -> "ClaudeDesignStoryModel":
        raise NotImplementedError("A Claude Design canvas is rendered from the story map; it is not read back.")

    # -- canvas ---------------------------------------------------------------------------

    def files(self) -> Dict[str, str]:
        return self.canvas().files()

    def canvas(self) -> DesignCanvas:
        """One story-map artboard holds every bar, card and thumbnail: one Play, one live page to draw."""
        canvas = DesignCanvas(self.name if self.name and self.name != "StoryModel" else "Story Map")
        canvas.add_page(self.story_map_page, "Story map")
        canvas.add_page(self.screens_page, "Story explorer")
        for page in ClaudeDesignUxMap.pages(self.screens, self._screen_files()):
            canvas.add_page(page["id"], page["name"])
        width, height, text = self._story_map()
        canvas.add_board("Main.dc.html", {"x": 0, "y": 0, "w": width, "h": height, "page": self.story_map_page,
                                          "title": "Story map", "is_interactive": True, "expand": "fill"}, text)
        canvas.add_board(f"{self.screens_folder}/explorer.dc.html", {"x": 0, "y": 0, "w": 1880, "h": 948, "page": self.screens_page,
                                                                     "title": "Story explorer", "is_interactive": True, "expand": "fill"}, self._explorer())
        for name, board in ClaudeDesignUxMap.boards(self.screens, self._screen_files()).items():
            canvas.add_board(name, board)
        return canvas

    def _story_map(self) -> tuple:
        """The story map artboard: its width, height, and file text."""
        explorer_href = f"/{self.screens_folder}/explorer.dc.html"
        parts: List[str] = []
        x = 0
        thumbs_top = ClaudeDesignEpic.header_height() + self.thumbs_gap
        bottom = ClaudeDesignEpic.header_height()
        spans: Dict[int, list] = {}
        for epic in self._leaf_epics():
            top = epic.top_epic()
            span = spans.setdefault(id(top), [top.name, x, x])
            span[2] = x + epic.column_width()
            parts.extend(epic.header_parts(x))
            for column, story in enumerate(epic.stories):
                left = x + column * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px)
                cells = self._thumbnails(story, left, thumbs_top, explorer_href)
                parts.extend(cells)
                if cells:
                    bottom = max(bottom, thumbs_top + len(cells) * (ClaudeDesignStory.thumb_px + ClaudeDesignStory.thumb_gap_px))
            x += epic.column_width() + self.sub_epic_gap
        parts = [box(left, 0, right - left, ClaudeDesignEpic.bar_height, LOOK["epic"], name) for name, left, right in spans.values()] + parts
        width = max(x - self.sub_epic_gap, 40) + 2 * self.margin
        height = bottom + 2 * self.margin
        body = f'<div style="position: absolute; left: {self.margin}px; top: {self.margin}px">' + "\n".join(parts) + "</div>"
        return width, height, artboard("Story map", width, height, body, style=f"body{{margin:0;background:{BACKGROUND}}}",
                                       root_style=f"background: {BACKGROUND}", head=FONTS, zoomable=True)

    def _leaf_epics(self) -> List[ClaudeDesignEpic]:
        found: List[ClaudeDesignEpic] = []
        for epic in self.epics:
            found.extend(epic.leaf_epics())
        return found

    def _thumbnails(self, story: ClaudeDesignStory, left: int, top: int, explorer_href: str) -> List[str]:
        """Under each story, its main screens, up to ``screens_per_story``, in the order the UX map lists them: the UX map
        names each story's main page first. Each opens the story explorer at the step it was captured on."""
        shown = story.shown_screens(self.screens)
        listed = {id(screen): index for index, screen in enumerate(self.screens)}
        shown.sort(key=lambda found: listed.get(id(found[2]), len(listed)))
        cells = []
        for row, (scenario, step, screen) in enumerate(shown[: self.screens_per_story]):
            place = {"story": story.name}
            if scenario is not None and scenario in story.scenarios:
                place.update({"scenario": scenario.name, "step": step.text})
            caption = f"{scenario.name} › {step.text}" if scenario is not None else story.name
            cells.append(thumbnail(left, top + row * (ClaudeDesignStory.thumb_px + ClaudeDesignStory.thumb_gap_px),
                                   ClaudeDesignStory.width_px, ClaudeDesignStory.thumb_px, caption, screen.image, f"{explorer_href}#{urlencode(place, quote_via=quote)}"))
        return cells

    def _prototypes(self) -> List[str]:
        return ClaudeDesignUxMap.prototype_names(self.screens)

    # -- explorer -------------------------------------------------------------------------

    def _explorer(self) -> str:
        tree = []
        for epic in self.epics:
            subs = epic.leaf_epics()
            tree.append({"n": epic.name, "u": [{"n": sub.name, "s": [self._story_entry(story) for story in sub.stories]}
                                               for sub in subs]})
        template = _EXPLORER_TEMPLATE.read_text(encoding="utf-8")
        heads = [f'<link rel="stylesheet" href="{href}">' for href in self._stylesheets()]
        heads += [f'<script src="../{script}"></script>' for script in self._fixture_scripts()]
        return (template.replace("__STYLESHEETS__", "\n".join(heads))
                .replace("__IMPORTS__", "\n".join(self._imports()))
                .replace("__DATA__", json.dumps(tree, ensure_ascii=False)))

    def _story_entry(self, story: ClaudeDesignStory) -> dict:
        scenarios = []
        for scenario in [*story.backgrounds, *story.scenarios]:
            groups: List[dict] = []
            waiting: List[str] = []
            prototype = ""
            for step in _steps_of(scenario):
                indent = "    " if step.keyword in ("And", "But") else ""
                waiting.append(f"{indent}{step.keyword} {step.text}")
                shown = [screen for screen in shown_on(step, self.screens) if not self._blank(screen)]
                prototype = prototype or next((stem(s.prototype) for s in shown if s.prototype), "")
                if shown:
                    groups.append({"x": "\n".join(waiting), "i": [f"../{s.image}" for s in shown if s.image]})
                    waiting = []
            if waiting and groups:
                groups[-1]["x"] += "\n" + "\n".join(waiting)
            elif waiting:
                groups.append({"x": "\n".join(waiting), "i": []})
            if not prototype and not any(group["i"] for group in groups):
                prototype, image = self._screen_of(scenario, story)
                if image:
                    groups[0]["i"] = [f"../{image}"]
            background = scenario in story.backgrounds
            scenarios.append({"n": "Background" if background else scenario.name, "b": background, "p": prototype, "t": groups,
                              "f": self.sources.get(scenario_key(scenario), "")})
        return {"n": story.name, "f": self.sources.get(story.name, ""), "c": scenarios}

    def _screen_of(self, scenario, story: ClaudeDesignStory) -> tuple:
        """A scenario whose steps show no screen shows its own ``shownOn`` screen, else its story's:
        that screen's prototype, else its screenshot."""
        own = shown_on(scenario, self.screens) or shown_on(story, self.screens)
        prototype = next((stem(screen.prototype) for screen in own if screen.prototype), "")
        image = next((screen.image for screen in own if screen.image and not self._blank(screen)), "")
        return prototype, image

    def _imports(self) -> List[str]:
        lines = []
        for prototype in self._prototypes():
            name = stem(prototype)
            lines.append(f'<sc-if value="{{{{live.{camel(name)}}}}}" hint-placeholder-val="{{{{ false }}}}">'
                         f'<dc-import name="{name}" story="{{{{storyName}}}}" scenario="{{{{scenarioName}}}}" go="{{{{goToStory}}}}" hint-size="1280px,900px" style="display: block; width: 100%; min-height: 100%"></dc-import></sc-if>')
        return lines

    def _screen_files(self) -> List[str]:
        """Screen artboards already in the canvas's screens folder: each needs a place on the Screens page."""
        folder = self.workspace / "project" / self.screens_folder if self.workspace else None
        if folder is None or not folder.is_dir():
            return []
        return [f"{self.screens_folder}/{path.name}" for path in sorted(folder.glob("*.dc.html")) if path.name != "explorer.dc.html"]

    fixture_scripts = ("fixtures/canvas-fixtures.js",)

    def _fixture_scripts(self) -> List[str]:
        """A pattern's fixtures bundle, when the canvas has one: a screen inside the explorer loads its fixtures from it."""
        root = self.workspace / "project" if self.workspace else None
        return [script for script in self.fixture_scripts if root is not None and (root / script).is_file()]

    def _stylesheets(self) -> List[str]:
        """The stylesheets the prototype screens link, so a screen drawn inside the explorer keeps its own look."""
        found: List[str] = []
        root = self.workspace / "project" if self.workspace else None
        for prototype in [*self._prototypes(), *self._screen_files()]:
            path = root / prototype if root else None
            if path is None or not path.is_file():
                continue
            for href in re.findall(r'<link rel="stylesheet" href="([^"]+)"', path.read_text(encoding="utf-8")):
                if href not in found:
                    found.append(href)
        return found

    def _blank(self, screen) -> bool:
        root = self.workspace / "project" if self.workspace else None
        if root is None or not screen.image:
            return False
        path = root / screen.image
        return path.is_file() and path.stat().st_size < self.blank_image_bytes

    def _screens(self, screens) -> List:
        if screens is None and getattr(self, "workspace", None) is not None:
            from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap

            screens = JsonUxMap.from_workspace(self.workspace) or JsonUxMap.from_workspace(self.workspace.parent)
        if screens is None:
            return []
        return list(getattr(screens, "screens", screens))


def shown_on(node, screens: Iterable) -> List:
    """The screens a step, scenario or story is shown on: its ``shownOn`` edges, else the screens that list its key."""
    practice = getattr(node, "practice", None)
    edged = [edge.child for edge in practice.edges_from(_SHOWN_ON, node)] if practice is not None else []
    if edged:
        return edged
    kind = node.semantic_type()
    if kind == "Step":
        key, names = step_key(node), "step_names"
    elif kind in ("Scenario", "Background"):
        key, names = scenario_key(node), "scenario_names"
    else:
        key, names = node.name, "story_names"
    return [screen for screen in screens if key in list(getattr(screen, names, []) or [])]


def _steps_of(scenario) -> List:
    found = []
    for step in scenario.steps:
        found.append(step)
        found.extend(getattr(step, "ands", []) or [])
    return found
