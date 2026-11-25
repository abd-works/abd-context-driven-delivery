"""One project's story canvas, rendered in one call: what the UX practice's mockup fidelity runs in the claude_design
format.

``ProjectStoryCanvas(project_root, ux_root, stories_root, fixtures).render(screens)``:

1. reads the story map below the Stories practice's root, with each story's scenario file, and the UX map
   (``<ux root>/ux.json``);
2. takes the working version of the UX root's design canvas (``CanvasVersions.working()``), the latest while it is
   unpublished, else a new one copied from it, or the latest itself when ``versions.json`` keeps one canvas
   (``"keep_one": true``);
3. builds the active pattern's fixtures bundle into ``project/fixtures/canvas-fixtures.js``, and stops with
   *FixturesNotBuilt*, rendering nothing, when it cannot be built (``stop-when-fixtures-fail``);
4. copies the files each screen's markup source names (*ScreenFiles*: a ported canvas's component and the scripts
   and stylesheets it loads) into ``project/``, writes each story's prototype screen (*StoryScreen*) to
   ``project/screens/<slug>.dc.html`` and names it as that screen's prototype in ``ux.json``;
5. renders the story map and the story explorer (*ClaudeDesignStoryMap*), whose step groups CDD derives from the
   scenarios, with each story's and scenario's ``path:line`` in its scenario file for the explorer's open request;
6. walks the screens at every step group and writes the report to ``walk.md`` in the version's folder.

See ``story_canvas.md`` beside this file, *Steps*.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping, Optional, Protocol, Sequence, TextIO

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap
from cdd_guidance.practices.stories.model.story_map import StoryMap
from cdd_guidance.practices.stories.model.story_tree import StoryTree
from cdd_guidance.practices.ux.model.claude_design.screen_walk import StoryCanvasWalk
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from harness.design_canvas.versions import CanvasVersion, CanvasVersions

FIXTURES_FILE = "fixtures/canvas-fixtures.js"
SCREENS_FOLDER = "screens"
UX_MAP_FILE = "ux.json"
WALK_FILE = "walk.md"
_STORY_HEADING = re.compile(r"^#+\s+Story:\s*(.+?)\s*$")


class CanvasFixtures(Protocol):
    """What builds a pattern's fixtures bundle: every story's scenarios, run through the real domain, in one script."""

    def build(self, story_names: Sequence[str], out_file: Path) -> Path: ...


class FixturesNotBuilt(RuntimeError):
    """The fixtures bundle could not be built, so the canvas is not rendered: screens drawn without it would show
    whatever an agent typed in, not what the stories hold (``stop-when-fixtures-fail``)."""


class ScreenNotOnUxMap(ValueError):
    """A prototype screen was handed for a slug the UX map holds no screen for, so no story would show it."""


class StoryMapNotFound(FileNotFoundError):
    """The Stories practice's root holds no markdown story map to draw the canvas from."""


class NoCanvasFixtures:
    """The fixtures builder of a session that overlays no pattern able to build canvas fixtures: building stops."""

    def __init__(self, overlays: Sequence[str]) -> None:
        self.overlays = list(overlays)

    def build(self, story_names: Sequence[str], out_file: Path) -> Path:
        chosen = ", ".join(self.overlays) or "none"
        raise FixturesNotBuilt(
            f"No pattern the session overlays builds canvas fixtures (overlays: {chosen}). Overlay the project's stack "
            "pattern, such as lern_domain_driven, so the screens draw each scenario's fixture through the real domain.")


class WalkReport(Protocol):
    @property
    def misses(self) -> Sequence[str]: ...

    def write(self, path: Path) -> Path: ...


@dataclass(frozen=True)
class RenderedStoryCanvas:
    """What one render left: the canvas version it rendered into, the files it wrote there, and the walk of its
    screens, saved at ``walk_file``."""

    version: CanvasVersion
    files: list
    walk: WalkReport
    walk_file: Path

    def summary(self, name: str) -> str:
        """The render in a few lines: where it went, the walk's misses, and the title to publish it under."""
        lines = [f"Rendered {len(self.files)} canvas files into {self.version.folder}.",
                 f"Walk: {self.walk_file} ({len(self.walk.misses)} value(s) the screens leave out)."]
        lines += [f"  - {miss}" for miss in self.walk.misses]
        if self.version.link is not None:
            lines.append(f"Publish it again at {self.version.link}, the canvas this project keeps updating in place, after reading "
                         f"that canvas back for edits people made there, and record the link again with version.publish_at.")
        else:
            lines.append(f"Publish it as a new canvas titled {self.version.title(name)!r} and keep its link with version.publish_at.")
        return "\n".join(lines)

    def print_summary(self, name: str, out: Optional[TextIO] = None) -> None:
        """Print the summary to out (standard output by default), writing each character out's encoding cannot hold,
        such as a minus sign a step value quotes on a Windows console, as its escape (``\\u2212``)."""
        out = out or sys.stdout
        encoding = getattr(out, "encoding", None) or "utf-8"
        out.write(self.summary(name).encode(encoding, "backslashreplace").decode(encoding) + "\n")


@dataclass
class ProjectStoryCanvas:
    """A project's story canvas: the project's root, the UX practice's root (where the canvas versions and ``ux.json``
    live), the Stories practice's root (where the story map lives), and the pattern's fixtures builder."""

    project_root: Path
    ux_root: Path
    stories_root: Path
    fixtures: CanvasFixtures
    walk_type: type = field(default=StoryCanvasWalk)

    def render(self, screens: Optional[Mapping[str, StoryScreen]] = None) -> RenderedStoryCanvas:
        """Render the canvas into the working version, with screens, by UX-map slug, written beside the screens already
        there. Stops with *FixturesNotBuilt* before anything is rendered when the fixtures cannot be built."""
        screens = dict(screens or {})
        story_map = self.story_map()
        ux_document = self._ux_document()
        self._check_on_ux_map(screens, ux_document)
        version = CanvasVersions.in_practice_root(self.ux_root).working()
        project = version.folder / "project"
        self._build_fixtures(story_map, project / FIXTURES_FILE)
        self._write_screens(screens, project, ux_document)
        ux_map = JsonUxMap().parse(ux_document)
        setup = StoryCanvasSetup(workspace=str(version.folder), ux_map=ux_map, sources=self.sources(story_map))
        written = json.loads(ClaudeDesignStoryMap(setup=setup).render(story_map))
        for path, text in written.items():
            target = version.folder / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        report = self.walk_type(version).walk(story_map)
        walk_file = report.write(version.folder / WALK_FILE)
        return RenderedStoryCanvas(version, sorted(written), report, Path(walk_file))

    def story_map(self) -> StoryMap:
        """The story map below the Stories practice's root, with each story's scenario file."""
        story_map = MarkdownStoryMap().read_folder(self.stories_root, self.project_root)
        if story_map is None:
            raise StoryMapNotFound(f"{self.stories_root} holds no markdown story map to draw the story canvas from.")
        return story_map

    def sources(self, story_map: StoryMap) -> Dict[str, str]:
        """Where each story (``Story``) and scenario (``Story › Scenario``) starts in its scenario file, as an absolute
        ``path:line``: a story at its ``Story:`` heading, a scenario at its own heading."""
        found: Dict[str, str] = {}
        for story in story_map.descendants.stories():
            for scenario in story.scenarios:
                source = scenario.source
                if source is None or not source.file:
                    continue
                file = (self.project_root / source.file).resolve()
                found[StoryTree.key_of(scenario)] = f"{file.as_posix()}:{source.start_line}"
                if story.name not in found:
                    found[story.name] = f"{file.as_posix()}:{self._story_heading_line(file, story.name)}"
        return found

    @staticmethod
    def _story_heading_line(file: Path, name: str) -> int:
        """The line of the story's ``Story:`` heading in its scenario file, else the file's first line."""
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            heading = _STORY_HEADING.match(line)
            if heading and heading.group(1) == name:
                return number
        return 1

    def _build_fixtures(self, story_map: StoryMap, out_file: Path) -> None:
        stories = [story.name for story in story_map.descendants.stories()]
        try:
            self.fixtures.build(stories, out_file)
        except FixturesNotBuilt:
            raise
        except Exception as failed:
            detail = getattr(failed, "stderr", None) or str(failed)
            raise FixturesNotBuilt(
                f"The canvas fixtures bundle ({out_file}) could not be built, so the story canvas is not rendered:\n"
                f"{type(failed).__name__}: {str(detail).strip()}") from failed

    @property
    def _ux_map_file(self) -> Path:
        return self.ux_root / UX_MAP_FILE

    def _ux_document(self) -> dict:
        return json.loads(self._ux_map_file.read_text(encoding="utf-8"))

    @staticmethod
    def _check_on_ux_map(screens: Mapping[str, StoryScreen], ux_document: dict) -> None:
        slugs = {record.get("slug") or record.get("name") for record in ux_document.get("screens", [])}
        missing = [slug for slug in screens if slug not in slugs]
        if missing:
            raise ScreenNotOnUxMap(f"The UX map holds no screen for {', '.join(missing)}; add the screen to ux.json first.")

    def _write_screens(self, screens: Mapping[str, StoryScreen], project: Path, ux_document: dict) -> None:
        """Copy the files each screen's markup needs, once for each markup, then write each screen into the version
        and name it as its UX-map screen's prototype, keeping every other field ux.json holds."""
        if not screens:
            return
        copied = []
        for markup in (screen.markup for screen in screens.values()):
            if markup not in copied:
                markup.copy_files(project)
                copied.append(markup)
        folder = project / SCREENS_FOLDER
        folder.mkdir(parents=True, exist_ok=True)
        for slug, screen in screens.items():
            (folder / f"{slug}.dc.html").write_text(screen.html, encoding="utf-8")
        for record in ux_document.get("screens", []):
            slug = record.get("slug") or record.get("name")
            if slug in screens:
                record["prototype"] = f"{SCREENS_FOLDER}/{slug}.dc.html"
        self._ux_map_file.write_text(json.dumps(ux_document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
