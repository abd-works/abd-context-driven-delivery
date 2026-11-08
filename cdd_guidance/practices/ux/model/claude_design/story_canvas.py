"""Claude Design story map: a canvas with the story map on one page and the screens on another.

The story map page holds one artboard: epic and sub-epic bars, actors, stories, and under each
story the thumbnail of its main screen. The screens page holds the story explorer and the
prototype screens. The canvas itself (pages, boards, canvas.json) is ``harness.design_canvas``;
render returns its files as JSON: ``{"project/<path>": "<file text>"}``.
"""

from __future__ import annotations

import html
import json
from functools import cached_property
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote, urlencode

from harness.design_canvas.canvas import DesignCanvas, artboard, box, stem, thumbnail
from harness.design_canvas.look import BACKGROUND, FONTS, LOOK
from cdd_guidance.practices.ux.model.claude_design.nodes import ClaudeDesignUxMap
from cdd_guidance.practices.ux.model.ux_map import UxMap
from harness.annotations.name import Name
from cdd_guidance.practices.ux.model.story_link import key_of

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Story, StoryModel

_EXPLORER_TEMPLATE = Path(__file__).with_name("explorer.dc.html")
_SHOWN_ON = "shownOn"


class ClaudeDesignEpic(DiagramEpic):
    """An epic or sub-epic: its bars over its stories' columns, at the drawio's own scale."""

    bar_height = 60
    sub_bar_height = 70
    bar_gap = 20

    def column_width(self) -> int:
        count = max(len(self.stories), 1)
        return count * ClaudeDesignStory.width_px + (count - 1) * ClaudeDesignStory.gap_px

    def header_parts(self, left: int) -> List[str]:
        """The sub-epic bar and each story's actor and card, from *left* on the story map. The epic bar spans its sub-epics; the map draws it."""
        width = self.column_width()
        top = self.top_epic
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
        """Each (scenario, step, screen) this story's steps are shown on, in scenario order, then each screen that
        shows the story itself as (None, None, screen); once per screen image."""
        seen: set = set()
        found: List[tuple] = []
        story_screens = [(None, None, screen) for screen in screens if screen.lists(self)]
        for scenario, step, screen in [*self._step_screens(screens), *story_screens]:
            marker = screen.image or screen.name
            if marker not in seen:
                seen.add(marker)
                found.append((scenario, step, screen))
        return found

    def _step_screens(self, screens: List) -> Iterable[tuple]:
        for scenario in [*self.backgrounds, *self.scenarios]:
            for step in _steps_of(scenario):
                for screen in shown_on(step, screens):
                    yield scenario, step, screen


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
    explorer_width = 1880
    explorer_height = 948

    def __init__(
        self,
        source: Optional[StoryModel] = None,
        graph=None,
        *,
        workspace: Optional[str] = None,
        ux_map: Optional[UxMap] = None,
        sources: Optional[Dict[str, str]] = None,
    ) -> None:
        """A canvas of source's story map, drawn with the screens of ux_map, the UX map the caller holds; the canvas
        keeps that map as a Claude Design map, which places the screens. *workspace* is the canvas root, whose
        ``project`` folder holds what people already made on the canvas. *sources* maps a story (``Story``) or
        scenario (``Story › Scenario``) to its ``path:line`` in the story code: the explorer offers to copy an "open in
        the file viewer" request for it."""
        super().__init__(source, graph)
        self.screen_map = self._screen_map(ux_map)
        self.sources = dict(sources or {})
        self.canvas = DesignCanvas(self.name if self.name and self.name != "StoryModel" else "Story Map",
                                   Path(workspace) / "project" if workspace else None)

    def render(
        self,
        canonical: Optional[StoryModel] = None,
        previous: Optional[str] = None,
        workspace: Optional[str] = None,
        ux_map: Optional[UxMap] = None,
        sources: Optional[Dict[str, str]] = None,
    ) -> str:
        """The canvas files as JSON, drawn on a new canvas of canonical (else of this map) made for this UX map and
        these sources, so this canvas keeps its own."""
        source = canonical if canonical is not None else self
        drawn = type(self)(source, workspace=workspace, ux_map=ux_map, sources=sources)
        return json.dumps(drawn.files(), indent=1, ensure_ascii=False)

    def parse(self, text: str) -> "ClaudeDesignStoryModel":
        raise NotImplementedError("A Claude Design canvas is rendered from the story map; it is not read back.")

    # -- canvas ---------------------------------------------------------------------------

    def files(self) -> Dict[str, str]:
        return self.drawn.files()

    @cached_property
    def drawn(self) -> DesignCanvas:
        """The canvas with this map drawn on it, drawn once. One story-map artboard holds every bar, card and
        thumbnail: one Play, one live page to draw."""
        canvas = self.canvas
        canvas.add_page(self.story_map_page, "Story map")
        canvas.add_page(self.screens_page, "Story explorer")
        for page in self.screen_map.pages(self._screen_files()):
            canvas.add_page(page["id"], page["name"])
        width, height, text = self._story_map()
        canvas.add_board("Main.dc.html", {"x": 0, "y": 0, "w": width, "h": height, "page": self.story_map_page,
                                          "title": "Story map", "is_interactive": True, "expand": "fill"}, text)
        canvas.add_board(f"{self.screens_folder}/explorer.dc.html", {"x": 0, "y": 0, "w": self.explorer_width, "h": self.explorer_height, "page": self.screens_page,
                                                                     "title": "Story explorer", "is_interactive": True, "expand": "fill"}, self._explorer())
        for name, board in self.screen_map.boards(self._screen_files()).items():
            canvas.add_board(name, board)
            focus = self._stories_shown_on(name)
            if focus:
                canvas.add_board(f"{self.context_folder}/{stem(name)}.dc.html",
                                 {"x": board["w"] + 80, "y": 0, "w": self.context_width, "h": board["h"], "page": board["page"],
                                  "title": "Stories"}, self._context_panel(focus, board["h"]))
        return canvas

    context_folder = "context"
    context_width = 560

    def _stories_shown_on(self, name: str) -> List[str]:
        """The stories whose screen is this artboard: the story-level edges of the screens that prototype it."""
        found: List[str] = []
        for screen in self.screen_map.screens:
            if screen.prototype and Path(screen.prototype).name == Path(name).name:
                found += [story for story in screen.story_keys if story not in found]
        return found

    def _context_panel(self, focus: List[str], height: int) -> str:
        """A read-only story panel for a screen's page: the whole hierarchy greyed and collapsed, except the stories
        the screen serves, opened to their scenarios and steps. Nothing in it navigates or edits."""
        lines: List[str] = []
        for epic in self.epics:
            lines.append(f'<div class="cx-epic">{html.escape(epic.name)}</div>')
            for sub in epic.leaf_epics():
                lines.append(f'<div class="cx-sub">{html.escape(sub.name)}</div>')
                for story in sub.stories:
                    if story.name not in focus:
                        lines.append(f'<div class="cx-story">{html.escape(story.name)}</div>')
                        continue
                    lines.append(f'<div class="cx-story cx-on">{html.escape(story.name)}</div>')
                    for scenario in self._story_entry(story)["c"]:
                        lines.append(f'<div class="cx-scenario">{html.escape(scenario["n"])}</div>')
                        steps = "\n".join(group["x"] for group in scenario["t"])
                        lines.append(f'<div class="cx-steps">{html.escape(steps)}</div>')
        style = (f"body{{margin:0;background:{BACKGROUND}}}"
                 ".cx-epic,.cx-sub{font:600 11px/1.6 'JetBrains Mono',ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em;color:#4A4A52;padding:4px 0}"
                 ".cx-sub{padding-left:12px}"
                 ".cx-story{font:500 13px/1.6 'Inter',system-ui,sans-serif;color:#4A4A52;padding:2px 0 2px 24px}"
                 f".cx-story.cx-on{{color:#E8E8ED;font-weight:600;box-shadow:inset 3px 0 0 {LOOK['epic']['color']};margin-top:6px}}"
                 ".cx-scenario{font:600 13px/1.6 'Inter',system-ui,sans-serif;color:#F2A07A;padding:6px 0 0 36px}"
                 ".cx-steps{font:400 12px/1.5 'JetBrains Mono',ui-monospace,monospace;color:#9B9BA8;white-space:pre-wrap;padding:2px 0 4px 48px}")
        body = ('<div style="position: absolute; inset: 0; overflow: auto; box-sizing: border-box; padding: 20px 20px 40px; '
                'background: #111113; border-left: 1px solid #2A2A2A">\n' + "\n".join(lines) + "\n</div>")
        return artboard("Stories", self.context_width, height, body, style=style, root_style=f"background: {BACKGROUND}", head=FONTS)

    def _story_map(self) -> tuple:
        """The story map artboard: its width, height, and file text."""
        explorer_href = f"/{self.screens_folder}/explorer.dc.html"
        parts: List[str] = []
        x = 0
        thumbs_top = ClaudeDesignEpic.header_height() + self.thumbs_gap
        bottom = ClaudeDesignEpic.header_height()
        spans: Dict[int, list] = {}
        for epic in self.leaf_epics():
            top = epic.top_epic
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

    def _thumbnails(self, story: ClaudeDesignStory, left: int, top: int, explorer_href: str) -> List[str]:
        """Under each story, its main screens, up to ``screens_per_story``, in the order the UX map lists them: the UX map
        names each story's main page first. Each opens the story explorer at the step it was captured on."""
        shown = story.shown_screens(self.screen_map.screens)
        listed = {id(screen): index for index, screen in enumerate(self.screen_map.screens)}
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
        return self.screen_map.prototype_names()

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
                shown = [screen for screen in shown_on(step, self.screen_map.screens) if not self._blank(screen)]
                prototype = prototype or next((stem(s.prototype) for s in shown if s.prototype), "")
                if shown:
                    groups.append({"x": "\n".join(waiting), "i": [f"../{s.image}" for s in shown if s.image]})
                    waiting = []
            if waiting and groups:
                groups[-1]["x"] += "\n" + "\n".join(waiting)
            elif waiting:
                groups.append({"x": "\n".join(waiting), "i": []})
            if not prototype:
                prototype, image = self._screen_of(scenario, story)
                if image and not any(group["i"] for group in groups):
                    groups[0]["i"] = [f"../{image}"]
            background = scenario in story.backgrounds
            scenarios.append({"n": "Background" if background else scenario.name, "b": background, "p": prototype, "t": groups,
                              "f": self.sources.get(key_of(scenario), "")})
        return {"n": story.name, "f": self.sources.get(story.name, ""), "c": scenarios}

    def _screen_of(self, scenario, story: ClaudeDesignStory) -> tuple:
        """A scenario whose steps show no screen shows its own ``shownOn`` screen, else its story's:
        that screen's prototype, else its screenshot."""
        own = shown_on(scenario, self.screen_map.screens) or shown_on(story, self.screen_map.screens)
        prototype = next((stem(screen.prototype) for screen in own if screen.prototype), "")
        image = next((screen.image for screen in own if screen.image and not self._blank(screen)), "")
        return prototype, image

    def _imports(self) -> List[str]:
        lines = []
        for prototype in self._prototypes():
            name = stem(prototype)
            lines.append(f'<sc-if value="{{{{live.{Name(name).camel}}}}}" hint-placeholder-val="{{{{ false }}}}">'
                         f'<dc-import name="{name}" story="{{{{storyName}}}}" scenario="{{{{scenarioName}}}}" go="{{{{goToStory}}}}" hint-size="1280px,900px" style="display: block; width: 100%; min-height: 100%"></dc-import></sc-if>')
        return lines

    def _screen_files(self) -> List[str]:
        """Screen artboards already in the canvas's screens folder: each needs a place on the Screens page."""
        explorer = f"{self.screens_folder}/explorer.dc.html"
        return [name for name in self.canvas.artboards_in(self.screens_folder) if name != explorer]

    fixture_scripts = ("fixtures/canvas-fixtures.js",)

    def _fixture_scripts(self) -> List[str]:
        """A pattern's fixtures bundle, when the canvas has one: a screen inside the explorer loads its fixtures from it."""
        return [script for script in self.fixture_scripts if self.canvas.holds(script)]

    def _stylesheets(self) -> List[str]:
        """The stylesheets the prototype screens link, so a screen drawn inside the explorer keeps its own look."""
        return self.canvas.stylesheets_linked_by([*self._prototypes(), *self._screen_files()])

    def _blank(self, screen) -> bool:
        size = self.canvas.size_of(screen.image) if screen.image else None
        return size is not None and size < self.blank_image_bytes

    def _screen_map(self, ux_map: Optional[UxMap]) -> ClaudeDesignUxMap:
        """The Claude Design map this canvas places its screens with: ux_map itself when it is one, else a copy."""
        if isinstance(ux_map, ClaudeDesignUxMap):
            return ux_map
        screens = ClaudeDesignUxMap.create()
        return screens.copy_of(ux_map) if ux_map is not None else screens


def shown_on(node, screens: Iterable) -> List:
    """The screens a step, scenario or story is shown on: its ``shownOn`` edges, else the screens that list it, which
    is how a story map drawn on its own graph finds the screens on the UX map's graph."""
    edged = [edge.child for edge in node.graph.edges_from(_SHOWN_ON, node)] if node.practice is not None else []
    if edged:
        return edged
    return [screen for screen in screens if screen.lists(node)]


def _steps_of(scenario) -> List:
    found = []
    for step in scenario.steps:
        found.append(step)
        found.extend(getattr(step, "ands", []) or [])
    return found
