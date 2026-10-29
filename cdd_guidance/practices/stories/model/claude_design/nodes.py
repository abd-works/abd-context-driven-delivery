"""Claude Design story map: a canvas with the story map on one page and the screens on another.

The story map page holds one header artboard per sub-epic (epic bar, sub-epic bar, actors,
stories) and, under each story, a thumbnail for every screen its steps are ``shownOn``.
The screens page holds the story explorer and the prototype screens. Render returns the
canvas files as JSON: ``{"project/<path>": "<file text>"}``.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from harness.graph.schema_edges import step_key

from cdd_guidance.practices.ux.model.claude_design.nodes import ClaudeDesignUxMap

from cdd_guidance.practices.stories.model.diagram_story_model import (
    DiagramEpic,
    DiagramStory,
    DiagramStoryModel,
)
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel

_EXPLORER_TEMPLATE = Path(__file__).with_name("explorer.dc.html")
_SHOWN_ON = "shownOn"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _text(value: str) -> str:
    return html.escape(value, quote=True)


class ClaudeDesignEpic(DiagramEpic):
    """An epic or sub-epic as a header artboard on the story map page."""

    bar_height = 240
    sub_bar_height = 280
    bar_gap = 80
    epic_font = 64
    sub_epic_font = 52
    radius = 24

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

    def artboard_name(self, first: bool) -> str:
        return "Main.dc.html" if first else f"story-map/{_slug(self.top_epic().name)}--{_slug(self.name)}.dc.html"

    def header_html(self, explorer_href: str) -> str:
        width = self.column_width()
        top = self.top_epic()
        parts = [_box(0, 0, width, self.bar_height, self.fill, self.stroke, self.epic_font, True, top.name, self.radius)]
        if self is not top:
            parts.append(_box(0, self.bar_height + self.bar_gap, width, self.sub_bar_height, self.nested_fill,
                              self.nested_stroke, self.sub_epic_font, True, self.name, self.radius + 4))
        for index, story in enumerate(self.stories):
            parts.extend(story.header_cells(index * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px),
                                            self._story_top(), explorer_href))
        return _page(f"Story map: {self.name}", width, self.header_height(), "\n".join(parts),
                     style="body{margin:0} a{color:#000000} a:hover{color:#000000}",
                     root_style="background: #ffffff; font-family: Helvetica, Arial, sans-serif; color: #000000")

    def _story_top(self) -> int:
        return self.bar_height + self.bar_gap + self.sub_bar_height + self.bar_gap

    def header_height(self) -> int:
        return self._story_top() + ClaudeDesignStory.actor_px + ClaudeDesignStory.actor_gap_px + ClaudeDesignStory.card_px


class ClaudeDesignStory(DiagramStory):
    """A story column: its actor and card in the header, then one thumbnail per screen its steps show."""

    width_px = 640
    gap_px = 120
    actor_px = 160
    actor_gap_px = 40
    card_px = 280
    thumb_px = 450
    thumb_gap_px = 120
    actor_font = 44
    card_font = 48

    def header_cells(self, left: int, top: int, explorer_href: str) -> List[str]:
        actor = (self.actors or ["Customer"])[0]
        person = ('<svg width="56" height="80" viewBox="0 0 14 20" aria-hidden="true" style="fill: none; stroke: #6c8ebf; '
                  'stroke-width: 1.5"><circle cx="7" cy="3.5" r="2.5"></circle><path d="M7 6v7M1 9h12M7 13l-5 6M7 13l5 6"></path></svg>')
        return [
            _box(left, top, self.width_px, self.actor_px, self.actor_fill, self.actor_stroke, self.actor_font, False, actor, 0, icon=person),
            _box(left, top + self.actor_px + self.actor_gap_px, self.width_px, self.card_px, self.fill, self.stroke,
                 self.card_font, False, self.name, 0, href=explorer_href),
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
        return found


class ClaudeDesignStoryModel(DiagramStoryModel):
    """Claude Design canvas I/O. IS the format-typed tree root; render writes the canvas files."""

    epic_type = ClaudeDesignEpic
    story_type = ClaudeDesignStory
    story_map_page = "story-map"
    screens_page = ClaudeDesignUxMap.page
    screens_folder = ClaudeDesignUxMap.folder
    sub_epic_gap = 240
    thumbs_gap = 320
    blank_image_bytes = 10000

    def render(
        self,
        canonical: Optional[StoryModel] = None,
        previous: Optional[str] = None,
        workspace: Optional[str] = None,
        screens=None,
    ) -> str:
        """The canvas files as JSON. *screens* is a UxMap (or its screens); with only a *workspace*
        (the canvas root), its ``ux-map.json`` supplies them."""
        source = canonical if canonical is not None else self
        drawn = source if isinstance(source, ClaudeDesignStoryModel) else type(self)(source)
        drawn.workspace = Path(workspace) if workspace else None
        drawn.screens = drawn._screens(screens)
        return json.dumps(drawn.files(), indent=1, ensure_ascii=False)

    def parse(self, text: str) -> "ClaudeDesignStoryModel":
        raise NotImplementedError("A Claude Design canvas is rendered from the story map; it is not read back.")

    # -- canvas ---------------------------------------------------------------------------

    def files(self) -> Dict[str, str]:
        files: Dict[str, str] = {}
        boards: Dict[str, dict] = {}
        order: List[str] = []
        explorer_name = f"{self.screens_folder}/explorer.dc.html"
        explorer_href = f"/{explorer_name}"
        x = 0
        for index, epic in enumerate(self._leaf_epics()):
            name = epic.artboard_name(index == 0)
            files[f"project/{name}"] = epic.header_html(explorer_href)
            height = epic.header_height()
            boards[name] = {"x": x, "y": 0, "w": epic.column_width(), "h": height, "page": self.story_map_page,
                            "title": f"{epic.top_epic().name} › {epic.name}", "is_interactive": True}
            order.append(name)
            for column, story in enumerate(epic.stories):
                left = x + column * (ClaudeDesignStory.width_px + ClaudeDesignStory.gap_px)
                self._thumbnails(story, left, height + self.thumbs_gap, explorer_href, files, boards, order)
            x += epic.column_width() + self.sub_epic_gap
        files[f"project/{explorer_name}"] = self._explorer()
        boards[explorer_name] = {"x": 0, "y": 0, "w": 1880, "h": 948, "page": self.screens_page,
                                 "title": "Story explorer", "is_interactive": True}
        order.append(explorer_name)
        for name, board in ClaudeDesignUxMap.boards(self.screens).items():
            boards[name] = board
            order.append(name)
        files["project/canvas.json"] = json.dumps({
            "v": 3,
            "createdOnFiles": {"v": 1, "at": "2026-10-28T18:00:00Z"},
            "title": self.name if self.name and self.name != "StoryModel" else "Story Map",
            "launch": {"view": "canvas", "page": self.story_map_page},
            "pages": [{"id": self.story_map_page, "name": "Story map"}, {"id": self.screens_page, "name": "Screens"}],
            "boards": boards,
            "order": order,
            "notes": {},
            "designSystems": [],
        }, indent=1, ensure_ascii=False)
        return files

    def _leaf_epics(self) -> List[ClaudeDesignEpic]:
        found: List[ClaudeDesignEpic] = []
        for epic in self.epics:
            found.extend(epic.leaf_epics())
        return found

    def _thumbnails(self, story: ClaudeDesignStory, left: int, top: int, explorer_href: str,
                    files: Dict[str, str], boards: Dict[str, dict], order: List[str]) -> None:
        for row, (scenario, step, screen) in enumerate(story.shown_screens(self.screens)):
            name = f"story-map/{_slug(story.name)}-{row + 1:02d}.dc.html"
            title = f"{story.name} › {scenario.name} › {step.text}"
            href = f"/{self.screens_folder}/{Path(screen.prototype).name}" if screen.prototype else explorer_href
            image = f"../{screen.image}" if screen.image else ""
            files[f"project/{name}"] = _thumbnail(title, image, href)
            boards[name] = {"x": left, "y": top + row * (ClaudeDesignStory.thumb_px + ClaudeDesignStory.thumb_gap_px),
                            "w": ClaudeDesignStory.width_px, "h": ClaudeDesignStory.thumb_px,
                            "page": self.story_map_page, "title": title[:240], "is_interactive": True}
            order.append(name)

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
        return (template.replace("__STYLESHEETS__", "\n".join(f'<link rel="stylesheet" href="{href}">' for href in self._stylesheets()))
                .replace("__IMPORTS__", "\n".join(self._imports()))
                .replace("__DATA__", json.dumps(tree, ensure_ascii=False)))

    def _story_entry(self, story: ClaudeDesignStory) -> dict:
        scenarios = []
        for scenario in [*story.backgrounds, *story.scenarios]:
            groups: List[dict] = []
            waiting: List[str] = []
            prototype = ""
            for step in _steps_of(scenario):
                waiting.append(step.text)
                shown = [screen for screen in shown_on(step, self.screens) if not self._blank(screen)]
                prototype = prototype or next((_stem(s.prototype) for s in shown if s.prototype), "")
                if shown:
                    groups.append({"x": "\n".join(waiting), "i": [f"../{s.image}" for s in shown if s.image]})
                    waiting = []
            if waiting and groups:
                groups[-1]["x"] += "\n" + "\n".join(waiting)
            elif waiting:
                groups.append({"x": "\n".join(waiting), "i": []})
            scenarios.append({"n": scenario.name, "p": prototype, "t": groups})
        return {"n": story.name, "c": scenarios}

    def _imports(self) -> List[str]:
        lines = []
        for prototype in self._prototypes():
            stem = _stem(prototype)
            lines.append(f'<sc-if value="{{{{live.{_camel(stem)}}}}}" hint-placeholder-val="{{{{ false }}}}">'
                         f'<dc-import name="{stem}" hint-size="1280px,900px"></dc-import></sc-if>')
        return lines

    def _stylesheets(self) -> List[str]:
        """The stylesheets the prototype screens link, so a screen drawn inside the explorer keeps its own look."""
        found: List[str] = []
        root = self.workspace / "project" if self.workspace else None
        for prototype in self._prototypes():
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

            screens = JsonUxMap.from_workspace(self.workspace)
        if screens is None:
            return []
        return list(getattr(screens, "screens", screens))


def shown_on(step, screens: Iterable) -> List:
    """The screens a step is shown on: its ``shownOn`` edges, else the screens that list its step key."""
    practice = getattr(step, "practice", None)
    edged = [edge.child for edge in practice.edges_from(_SHOWN_ON, step)] if practice is not None else []
    if edged:
        return edged
    key = step_key(step)
    return [screen for screen in screens if key in list(getattr(screen, "step_names", []) or [])]


def _steps_of(scenario) -> List:
    found = []
    for step in scenario.steps:
        found.append(step)
        found.extend(getattr(step, "ands", []) or [])
    return found


def _stem(path: str) -> str:
    """A canvas file name without its folder or its .dc.html ending: the name a dc-import uses."""
    return Path(path).name.removesuffix(".dc.html")


def _camel(stem: str) -> str:
    head, *rest = stem.split("-")
    return head + "".join(part.capitalize() for part in rest)


def _box(left, top, width, height, fill, stroke, size, bold, text, radius, href=None, icon="") -> str:
    tag = "a" if href else "div"
    link = f' href="{href}"' if href else ""
    weight = "font-weight: 700; " if bold else ""
    return (f'<{tag}{link} style="position: absolute; left: {left}px; top: {top}px; width: {width}px; height: {height}px; '
            f'box-sizing: border-box; padding: 16px; gap: 16px; display: flex; align-items: center; justify-content: center; '
            f'text-align: center; background: {fill}; border: 4px solid {stroke}; border-radius: {radius}px; font-size: {size}px; '
            f'{weight}color: #000000; text-decoration: none">{icon}<span>{_text(text)}</span></{tag}>')


def _page(title: str, width: int, height: int, body: str, style: str, root_style: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{_text(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet><style>{style}</style></helmet>
<div style="position: relative; width: {width}px; height: {height}px; {root_style}">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{width},"height":{height}}}}}'>
class Component extends DCLogic {{
renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""


def _thumbnail(title: str, image: str, href: str) -> str:
    picture = (f'<img src="{image}" alt="{_text(title)}" style="display: block; width: 640px; height: 450px">' if image
               else '<span style="display: flex; width: 640px; height: 450px; align-items: center; justify-content: center; '
                    'color: #666666; font-family: Helvetica, Arial, sans-serif">No screenshot</span>')
    return _page(title, ClaudeDesignStory.width_px, ClaudeDesignStory.thumb_px,
                 f'<a href="{href}" style="display: block; width: 640px; height: 450px; background: #ffffff">{picture}</a>',
                 style="body{margin:0}", root_style="background: #ffffff")
