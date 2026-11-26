"""Claude Design story map: a canvas with the story map on one page and the screens on another.

The story map page holds one artboard: epic and sub-epic bars, actors, stories, and under each
story the thumbnail of its main screen. The screens page holds the story explorer and the
prototype screens. The canvas itself (pages, boards, canvas.json) is ``harness.design_canvas``;
render returns its files as JSON: ``{"project/<path>": "<file text>"}``.
"""

from __future__ import annotations

import html
import json
import re
from functools import cached_property
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import quote, urlencode

from harness.design_canvas.canvas import Artboard, DesignCanvas, Place, artboard_stem
from cdd_guidance.practices.ux.model.claude_design.class_cards import ClassCards
from cdd_guidance.practices.ux.model.claude_design.look import BACKGROUND, FONTS, LOOK
from cdd_guidance.practices.ux.model.claude_design.nodes import ClaudeDesignUxMap
from cdd_guidance.practices.ux.model.claude_design.screen_artboard import ScreenArtboard
from cdd_guidance.practices.ux.model.ux_map import UxMap
from harness.annotations.name import Name
from cdd_guidance.practices.stories.model.markdown.markup import plain_words
from cdd_guidance.practices.stories.model.story_tree import KEY_SEPARATOR, StoryTree

from cdd_guidance.practices.stories.model.diagram_story_map import (
    DiagramEpic,
    DiagramStory,
    DiagramStoryMap,
)
from cdd_guidance.practices.stories.model.story_map import Background, Scenario, Step, Story, StoryMap, StoryNode
from harness.graph.graph import Graph
from cdd_guidance.practices.ux.model.nodes import Screen
from harness.guidance.practice_formats import Written

_EXPLORER_TEMPLATE = Path(__file__).with_name("explorer.dc.html")
_SHOWN_ON = "shownOn"
_CONTEXT_PANEL_STYLE = (
    f"body{{margin:0;background:{BACKGROUND}}}"
    ".cx-epic,.cx-sub{font:600 11px/1.6 'JetBrains Mono',ui-monospace,monospace;text-transform:uppercase;letter-spacing:.08em;color:#4A4A52;padding:4px 0}"
    ".cx-sub{padding-left:12px}"
    ".cx-story{font:500 13px/1.6 'Inter',system-ui,sans-serif;color:#4A4A52;padding:2px 0 2px 24px}"
    f".cx-story.cx-on{{color:#E8E8ED;font-weight:600;box-shadow:inset 3px 0 0 {LOOK['epic']['color']};margin-top:6px}}"
    ".cx-scenario{font:600 13px/1.6 'Inter',system-ui,sans-serif;color:#F2A07A;padding:6px 0 0 36px}"
    ".cx-steps{font:400 12px/1.5 'JetBrains Mono',ui-monospace,monospace;color:#9B9BA8;white-space:pre-wrap;padding:2px 0 4px 48px}"
)
"""The context panel's look: the hierarchy greyed, and the stories the screen serves picked out."""


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
            Place(left, top, self.width_px, self.actor_px).card(LOOK["actor"], actor, icon=person),
            Place(left, top + self.actor_px + self.actor_gap_px, self.width_px, self.card_px).card(LOOK["story"], self.name),
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


class ClaudeDesignEpic(DiagramEpic):
    """An epic or sub-epic: its bars over its stories' columns, at the drawio's own scale."""

    story_class = ClaudeDesignStory
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
            parts.append(Place(left, self.bar_height + self.bar_gap, width, self.sub_bar_height).card(LOOK["sub_epic"], self.name))
        for index, story in enumerate(self.stories):
            parts.extend(story.header_cells(left + index * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px), self.story_top))
        return parts

    story_top = bar_height + bar_gap + sub_bar_height + bar_gap
    """Where the story actors and cards start: under the epic bar and the sub-epic bar."""
    header_height = story_top + ClaudeDesignStory.actor_px + ClaudeDesignStory.actor_gap_px + ClaudeDesignStory.card_px
    """Where the bars, actors, and cards end and the thumbnails begin."""


def source_key(story: "Story", scenario: "Scenario | Background") -> str:
    """The key a canvas's ``sources`` hold scenario's location under: ``Story › Scenario``, and for each later scenario
    of story with the same name, such as one a shared story file and its screen spec both write, that key with its
    place among them (``#2``), so each is opened in the file that writes it."""
    same_named = [own for own in story.scenarios if own.name == scenario.name]
    place = next((at for at, own in enumerate(same_named, start=1) if own is scenario), 1)
    key = StoryTree.key_of(scenario)
    return key if place == 1 else f"{key} #{place}"


class StoryCanvasSetup:
    """What a story canvas is drawn with besides its story map: the canvas root (``workspace``), whose ``project``
    folder holds what people already made on the canvas; the UX map whose screens it shows, the one the caller holds;
    and where each story (``Story``) and scenario (``Story › Scenario``) sits in the story code (``sources``, its
    ``path:line``), which the explorer offers to copy as an "open in the file viewer" request; the canvas's *title*,
    the name its version is published under (``ux-mockup``), so the canvas names itself as its file does; and
    *files_root*, the folder the story map's nodes name their files from (the project's root), where the class cards
    the steps' domain terms open are read from the model files they link."""

    def __init__(self, workspace: Optional[str] = None, ux_map: Optional[UxMap] = None, sources: Optional[Dict[str, str]] = None,
                 title: str = "", files_root: Optional[Path] = None) -> None:
        self.title = title
        self.files_root = files_root
        self.ux_map = ux_map
        self.sources = dict(sources or {})
        self.project = Path(workspace) / "project" if workspace else None


class ClaudeDesignStoryMap(DiagramStoryMap):
    """Claude Design canvas I/O. IS the format-typed tree root; render writes the canvas files."""

    epic_class = ClaudeDesignEpic
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

    def __init__(self, graph: Optional[Graph] = None, setup: Optional["StoryCanvasSetup"] = None) -> None:
        """A canvas drawn with what setup gives it; the canvas keeps setup's UX map as a Claude Design map, which places
        the screens."""
        super().__init__(graph)
        setup = setup or StoryCanvasSetup()
        # What every canvas this one renders is drawn with: the same UX map, sources, and project.
        self._setup = setup
        self.screen_map = self._screen_map(setup.ux_map)
        self.sources = dict(setup.sources)
        self.canvas = DesignCanvas(setup.title or (self.name if self.name and self.name != "StoryMap" else "Story Map"), setup.project)
        self.class_cards = ClassCards(setup.files_root)

    def blank(self) -> "ClaudeDesignStoryMap":
        """A canvas holding no story map, drawn with this canvas's setup."""
        return type(self)(setup=self._setup)

    def _copy_fields(self, original: StoryMap, copy_part) -> None:
        """Take original as every story map copy does, and the class cards its steps' domain terms open, read from the
        lines original's steps were read from, which a canvas's own steps no longer hold."""
        super()._copy_fields(original, copy_part)
        if isinstance(original, ClaudeDesignStoryMap):
            self.class_cards = original.class_cards
        else:
            self.class_cards = ClassCards(self._setup.files_root).read(_map_steps(original))

    def render(self, canonical: StoryMap, written: Written = Written()) -> str:
        """The canvas files as JSON, drawn on a new canvas of canonical made with this canvas's setup, so canonical
        keeps its own."""
        drawn = self.copy_of(canonical)
        return json.dumps(drawn.files(), indent=1, ensure_ascii=False)

    def parse(self, text: str, file: str = "") -> "ClaudeDesignStoryMap":
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
        for page in self.screen_map.pages(self._screen_files(), reserved=2):
            canvas.add_page(page["id"], page["name"])
        story_map = self._story_map()
        canvas.add(story_map, {"x": 0, "y": 0, "w": story_map.width, "h": story_map.height, "page": self.story_map_page,
                               "title": "Story map", "is_interactive": True, "expand": "fill"})
        canvas.place(f"{self.screens_folder}/explorer.dc.html", {"x": 0, "y": 0, "w": self.explorer_width, "h": self.explorer_height, "page": self.screens_page,
                                                                 "title": "Story explorer", "is_interactive": True, "expand": "fill"}, self._explorer())
        for name, board in self.screen_map.boards(self._screen_files(), reserved=2, sizes=self._screen_sizes()).items():
            canvas.place(name, board)
            self._add_context_panel(name)
        return canvas

    context_folder = "context"
    context_width = 560
    context_gap = 80
    """The space between a screen and the story panel beside it."""

    def _add_context_panel(self, name: str) -> None:
        """Beside the screen artboard name, on its page, the panel of the stories it serves; none when it serves none."""
        focus = self._stories_shown_on(name)
        if not focus:
            return
        board = self.canvas.placed(name)
        self.canvas.add(self._context_panel(focus, board["h"], f"{self.context_folder}/{artboard_stem(name)}.dc.html"),
                        {"x": board["x"] + board["w"] + self.context_gap, "y": board["y"], "w": self.context_width, "h": board["h"], "page": board["page"], "title": "Stories"})

    def _stories_shown_on(self, name: str) -> List[str]:
        """The stories whose screen is this artboard: the story-level edges of the screens that prototype it."""
        found: List[str] = []
        for screen in self.screen_map.screens:
            if screen.prototype and Path(screen.prototype).name == Path(name).name:
                found += [link.key for link in screen.story_links if link.key not in found]
        return found

    def _context_panel(self, focus: List[str], height: int, name: str) -> Artboard:
        """A read-only story panel for a screen's page: the whole hierarchy greyed and collapsed, except the stories
        the screen serves, opened to their scenarios and steps. Nothing in it navigates or edits."""
        lines: List[str] = []
        for epic in self.epics:
            lines.extend(self._context_epic_lines(epic, focus, 0))
        style = _CONTEXT_PANEL_STYLE
        body = ('<div style="position: absolute; inset: 0; overflow: auto; box-sizing: border-box; padding: 20px 20px 40px; '
                'background: #111113; border-left: 1px solid #2A2A2A">\n' + "\n".join(lines) + "\n</div>")
        return Artboard("Stories", self.context_width, height, body, style=style, root_style=f"background: {BACKGROUND}", head=FONTS, name=name)

    def _context_epic_lines(self, epic: ClaudeDesignEpic, focus: List[str], depth: int) -> List[str]:
        """An epic in the context panel at depth (0 for an epic of the map), then its sub-epics, as deep as the map
        nests them, then its stories."""
        if depth:
            lines = [f'<div class="cx-sub" style="padding-left: {12 * depth}px">{html.escape(epic.name)}</div>']
        else:
            lines = [f'<div class="cx-epic">{html.escape(epic.name)}</div>']
        for sub in epic.epics:
            lines.extend(self._context_epic_lines(sub, focus, depth + 1))
        lines.extend(line for story in epic.stories for line in self._context_story_lines(story, focus))
        return lines

    def _context_story_lines(self, story: ClaudeDesignStory, focus: List[str]) -> List[str]:
        """A story in the context panel: greyed and collapsed, or, when the screen serves it (in focus), opened to its
        scenarios and their steps."""
        if story.name not in focus:
            return [f'<div class="cx-story">{html.escape(story.name)}</div>']
        lines = [f'<div class="cx-story cx-on">{html.escape(story.name)}</div>']
        for scenario in self._story_entry(story)["c"]:
            lines.append(f'<div class="cx-scenario">{html.escape(scenario["n"])}</div>')
            steps = "\n".join(group["x"] for group in scenario["t"])
            lines.append(f'<div class="cx-steps">{html.escape(steps)}</div>')
        return lines

    def _story_map(self) -> Artboard:
        """The story map artboard, ``Main.dc.html``."""
        parts: List[str] = []
        x = 0
        bottom = ClaudeDesignEpic.header_height
        spans: Dict[int, list] = {}
        for epic in (leaf for top_epic in self.epics for leaf in top_epic.leaf_epics()):
            top = epic.top_epic
            span = spans.setdefault(id(top), [top.name, x, x])
            span[2] = x + epic.column_width()
            parts.extend(epic.header_parts(x))
            bottom = max(bottom, self._add_epic_thumbnails(epic, x, parts))
            x += epic.column_width() + self.sub_epic_gap
        parts = [Place(left, 0, right - left, ClaudeDesignEpic.bar_height).card(LOOK["epic"], name) for name, left, right in spans.values()] + parts
        width = max(x - self.sub_epic_gap, self.min_map_width) + 2 * self.margin
        height = bottom + 2 * self.margin
        body = f'<div style="position: absolute; left: {self.margin}px; top: {self.margin}px">' + "\n".join(parts) + "</div>"
        return Artboard("Story map", width, height, body, style=f"body{{margin:0;background:{BACKGROUND}}}",
                        root_style=f"background: {BACKGROUND}", head=FONTS, zoomable=True, name="Main.dc.html")

    min_map_width = 40
    """The narrowest story map, drawn when it holds no epic."""

    @property
    def thumbs_top(self) -> int:
        """Where the story thumbnails start, under the story cards."""
        return ClaudeDesignEpic.header_height + self.thumbs_gap

    @property
    def explorer_href(self) -> str:
        """Where a thumbnail opens the story explorer on the canvas."""
        return f"/{self.screens_folder}/explorer.dc.html"

    def _add_epic_thumbnails(self, epic: ClaudeDesignEpic, left: int, parts: List[str]) -> int:
        """Under each of epic's story columns from left, its thumbnails, added to parts; returns the lowest bottom they
        reach, or the header's when they draw none."""
        bottom = ClaudeDesignEpic.header_height
        for column, story in enumerate(epic.stories):
            cells = self._thumbnails(story, left + column * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px))
            parts.extend(cells)
            if cells:
                bottom = max(bottom, self.thumbs_top + len(cells) * (ClaudeDesignStory.thumb_px + ClaudeDesignStory.thumb_gap_px))
        return bottom

    def _thumbnails(self, story: ClaudeDesignStory, left: int) -> List[str]:
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
            caption = f"{scenario.name}{KEY_SEPARATOR}{step.text}" if scenario is not None else story.name
            top = self.thumbs_top + row * (ClaudeDesignStory.thumb_px + ClaudeDesignStory.thumb_gap_px)
            href = f"{self.explorer_href}#{urlencode(place, quote_via=quote)}"
            cells.append(Place(left, top, ClaudeDesignStory.width_px, ClaudeDesignStory.thumb_px).thumbnail(caption, screen.image, href))
        return cells

    def _prototypes(self) -> List[str]:
        return self.screen_map.prototype_names()

    # -- explorer -------------------------------------------------------------------------

    def _explorer(self) -> str:
        tree = [self._epic_entry(epic) for epic in self.epics]
        template = _EXPLORER_TEMPLATE.read_text(encoding="utf-8")
        heads = [f'<link rel="stylesheet" href="{href}">' for href in self._stylesheets()]
        heads += [f'<script src="{src}"></script>' for src in self._screen_scripts()]
        heads += [f'<script src="../{script}"></script>' for script in self._fixture_scripts()]
        return (template.replace("__STYLESHEETS__", "\n".join(heads))
                .replace("__IMPORTS__", "\n".join(self._imports()))
                .replace("__CARDS__", json.dumps(self.class_cards.shown(), ensure_ascii=False))
                .replace("__DATA__", json.dumps(tree, ensure_ascii=False)))

    def _epic_entry(self, epic: ClaudeDesignEpic) -> dict:
        """An epic as the explorer lists it: its sub-epics (``e``), each listed the same way, as deep as the story map
        nests them, and the stories directly under it (``s``)."""
        return {"n": epic.name, "e": [self._epic_entry(sub) for sub in epic.epics], "s": [self._story_entry(story) for story in epic.stories]}

    def _story_entry(self, story: ClaudeDesignStory) -> dict:
        scenarios = [self._scenario_entry(story, scenario) for scenario in [*story.backgrounds, *story.scenarios]]
        return {"n": story.name, "f": self.sources.get(story.name, ""), "c": scenarios}

    def _scenario_entry(self, story: ClaudeDesignStory, scenario: "Scenario | Background") -> dict:
        """A scenario as the explorer lists it: its steps grouped by the screen each group ends on, and the prototype
        it plays, else its own or its story's screen."""
        groups, prototype = self._step_groups(story, scenario)
        if not prototype:
            prototype, image = self._screen_of(scenario, story)
            if image and not any(group["i"] for group in groups):
                groups[0]["i"] = [f"../{image}"]
        background = scenario in story.backgrounds
        entry = {"n": "Background" if background else scenario.name, "b": background, "p": prototype, "t": groups,
                 "f": self.sources.get(source_key(story, scenario), "")}
        rows = _outline_rows(scenario, groups)
        if rows:
            entry["r"] = rows
        return entry

    def _step_groups(self, story: ClaudeDesignStory, scenario: "Scenario | Background") -> tuple[List[dict], str]:
        """The scenario's steps, grouped so each group ends on a step a screen shows, with that screen's images and the
        group's kind (``k``); and the first prototype those screens name. A screen that shows the story or the scenario
        but names none of its steps shows each step that ends an action (``one-group-per-action``). A group's kind is
        ``when`` when the Customer acts in it (it holds a When step), else the phase of its last step, so a screen
        knows on which group to type in what the Customer enters."""
        groups: List[_StepGroup] = []
        waiting = _StepGroup()
        prototype = ""
        unnamed = self._screens_naming_no_steps(story, scenario)
        ends = _action_ends(scenario) if unnamed else []
        for step, phase in _phased_steps(scenario):
            waiting.take(step, phase)
            named = shown_on(step, self.screen_map.screens)
            derived = [screen for screen in unnamed if screen not in named] if any(step is end for end in ends) else []
            shown = [screen for screen in [*named, *derived] if not self._blank(screen)]
            prototype = prototype or next((artboard_stem(s.prototype) for s in shown if s.prototype), "")
            if shown:
                waiting.images = [f"../{s.image}" for s in shown if s.image]
                groups.append(waiting)
                waiting = _StepGroup()
        if waiting.lines and groups:
            groups[-1].take_all(waiting)
        elif waiting.lines:
            groups.append(waiting)
        return [group.entry(self.class_cards) for group in groups], prototype

    def _screens_naming_no_steps(self, story: ClaudeDesignStory, scenario: "Scenario | Background") -> List[Screen]:
        """The screens that show the scenario or its story and name none of the steps they show, so CDD derives them."""
        screens = self.screen_map.screens
        found: List[Screen] = []
        for screen in [*shown_on(scenario, screens), *shown_on(story, screens)]:
            if not screen.step_keys and screen not in found:
                found.append(screen)
        return found

    def _screen_of(self, scenario: "Scenario | Background", story: ClaudeDesignStory) -> tuple:
        """A scenario whose steps show no screen shows its own ``shownOn`` screen, else its story's:
        that screen's prototype, else its screenshot."""
        own = shown_on(scenario, self.screen_map.screens) or shown_on(story, self.screen_map.screens)
        prototype = next((artboard_stem(screen.prototype) for screen in own if screen.prototype), "")
        image = next((screen.image for screen in own if screen.image and not self._blank(screen)), "")
        return prototype, image

    def _imports(self) -> List[str]:
        """Each prototype screen in the explorer's screen pane. The import fills the pane's width and the screen's own
        frame (StoryScreen, at the screen's width) centres itself in it, so it lays out as it does on its own artboard
        and the fixture bar at the pane's left stays clear of it; a screen that states no size fills the pane."""
        lines = []
        sizes = self._screen_sizes()
        for prototype in self._prototypes():
            name = artboard_stem(prototype)
            size = sizes.get(prototype)
            hint, style = (f"{size[0]}px,{size[1]}px", "display: block; width: 100%") if size else \
                ("1280px,900px", "display: block; width: 100%; min-height: 100%")
            lines.append(f'<sc-if value="{{{{live.{Name(name).camel}}}}}" hint-placeholder-val="{{{{ false }}}}">'
                         f'<dc-import name="{name}" story="{{{{storyName}}}}" scenario="{{{{scenarioName}}}}" go="{{{{goToStory}}}}" step="{{{{stepText}}}}" step-index="{{{{stepIndex}}}}" step-kind="{{{{stepKind}}}}" hint-size="{hint}" style="{style}"></dc-import></sc-if>')
        return lines

    def _screen_sizes(self) -> Dict[str, tuple]:
        """Each screen artboard's own width and height, by its name, as the artboard the project holds states them
        (``$preview``); a screen the project does not hold, or that states no size, is left out."""
        sizes = {}
        for name in self.screen_map.names(self._screen_files()):
            size = ScreenArtboard.at(self.canvas.project.folder / name).preview_size if self.canvas.project.holds(name) else None
            if size:
                sizes[name] = size
        return sizes

    def _screen_files(self) -> List[str]:
        """Screen artboards already in the canvas's screens folder: each needs a place on the Screens page."""
        explorer = f"{self.screens_folder}/explorer.dc.html"
        return [name for name in self.canvas.project.artboards_in(self.screens_folder) if name != explorer]

    fixture_scripts = ("fixtures/canvas-fixtures.js",)

    def _fixture_scripts(self) -> List[str]:
        """A pattern's fixtures bundle, when the canvas has one: a screen inside the explorer loads its fixtures from it."""
        return [script for script in self.fixture_scripts if self.canvas.project.holds(script)]

    def _stylesheets(self) -> List[str]:
        """The stylesheets the prototype screens link, so a screen drawn inside the explorer keeps its own look."""
        return self.canvas.project.stylesheets_linked_by([*self._prototypes(), *self._screen_files()])

    def _screen_scripts(self) -> List[str]:
        """The scripts the prototype screens load, such as a design system's components, so a screen drawn inside the
        explorer finds them; the fixtures bundle is loaded on its own."""
        fixtures = {f"../{script}" for script in self.fixture_scripts}
        return [src for src in self.canvas.project.scripts_linked_by([*self._prototypes(), *self._screen_files()]) if src not in fixtures]

    def _blank(self, screen: Screen) -> bool:
        size = self.canvas.project.size_of(screen.image) if screen.image else None
        return size is not None and size < self.blank_image_bytes

    def _screen_map(self, ux_map: Optional[UxMap]) -> ClaudeDesignUxMap:
        """The Claude Design map this canvas places its screens with: ux_map itself when it is one, else a copy."""
        if isinstance(ux_map, ClaudeDesignUxMap):
            return ux_map
        screens = ClaudeDesignUxMap.create()
        return screens.copy_of(ux_map) if ux_map is not None else screens


def shown_on(node: StoryNode, screens: Iterable[Screen]) -> List[Screen]:
    """The screens a step, scenario or story is shown on: its ``shownOn`` edges, else the screens that list it, which
    is how a story map drawn on its own graph finds the screens on the UX map's graph."""
    edged = [edge.child for edge in node.graph.edges.from_parent(_SHOWN_ON, node)] if node.practice is not None else []
    if edged:
        return edged
    return [screen for screen in screens if screen.lists(node)]


class _StepGroup:
    """The steps the explorer lists as one group, being gathered: each step's line in plain words (an And or But set
    in), its phase, the realization each realized step's call graph gives, under its line, and the images of the screen
    the group ends on."""

    def __init__(self) -> None:
        self.lines: List[str] = []
        self.phases: List[str] = []
        self.realized: List[str] = []
        self.images: List[str] = []

    def take(self, step: Step, phase: str) -> None:
        line = f"{step.keyword} {plain_words(step.text)}"
        self.lines.append(("    " if step.keyword in ("And", "But") else "") + line)
        self.phases.append(phase)
        if step.call_graph:
            self.realized.append(f"{line}\n{step.call_graph.block()}")

    def take_all(self, later: "_StepGroup") -> None:
        """Take the steps of later, which end on no screen, after this group's own."""
        self.lines += later.lines
        self.phases += later.phases
        self.realized += later.realized

    def entry(self, class_cards: ClassCards) -> dict:
        """The group as the explorer's tree holds it: its text (``x``), images (``i``) and kind (``k``); the domain
        terms its text names, each with the key of its class card (``m``), and its realizations (``z``), when it has
        any."""
        text = "\n".join(self.lines)
        entry = {"x": text, "i": self.images, "k": _kind_of(self.phases)}
        terms = class_cards.terms_in(text)
        if terms:
            entry["m"] = terms
        if self.realized:
            entry["z"] = "\n\n".join(self.realized)
        return entry


def _map_steps(story_map: StoryMap) -> List[Step]:
    """Every step of every story's Backgrounds and scenarios, each And or But after the step it continues."""
    return [step for story in story_map.descendants.stories() for scenario in [*story.backgrounds, *story.scenarios]
            for step in _steps_of(scenario)]


def _steps_of(scenario: "Scenario | Background") -> List[Step]:
    found: List[Step] = []
    for step in scenario.steps:
        found.append(step)
        found.extend(getattr(step, "ands", []) or [])
    return found


_PLACEHOLDER = re.compile(r"\$?\{[^}]+\}|<[^>]+>")


def _outline_rows(scenario: "Scenario | Background", groups: List[dict]) -> Dict[str, Dict[str, str]]:
    """An outline's Examples table as the explorer fills its steps from it: each row, by its name (its ``example``
    column), with every column's value in plain words. A scenario whose steps name no placeholder has none."""
    examples = getattr(scenario, "examples", None) or {}
    if not examples or not any(_PLACEHOLDER.search(group["x"]) for group in groups):
        return {}
    return {plain_words(example.name): {column: plain_words(value) for column, value in example.row.items()}
            for example in examples.values()}


def _phased_steps(scenario: "Scenario | Background") -> List[tuple]:
    """Each step of the scenario, in order, with its phase: given, when or then. An And or But takes the phase of the
    step it continues."""
    phased: List[tuple] = []
    for step in scenario.steps:
        phased.append((step, step.phase))
        phased.extend((extra, extra.phase or step.phase) for extra in getattr(step, "ands", []) or [])
    return phased


def _kind_of(phases: List[str]) -> str:
    """A step group's kind from its steps' phases: ``when`` when it holds a When step, else its last step's phase."""
    return "when" if "when" in phases else next((phase for phase in reversed(phases) if phase), "")


def _action_ends(scenario: "Scenario | Background") -> List[Step]:
    """The steps a screen shows when the UX map names none: the step before each Then that opens a run of Thens, and
    the scenario's last step, so each action and its outcome is one step group."""
    phased = _phased_steps(scenario)
    ends = [phased[index - 1][0] for index, (_, phase) in enumerate(phased)
            if index and phase == "then" and phased[index - 1][1] != "then"]
    if phased and not any(phased[-1][0] is end for end in ends):
        ends.append(phased[-1][0])
    return ends
