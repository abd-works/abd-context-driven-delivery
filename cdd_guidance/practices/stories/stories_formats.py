"""Stories' formats: story tests in code are read as files beside the story map that names them."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from harness.guidance.practice_formats import PracticeFormats, RenderRequest

from cdd_guidance.practices.stories.model.diagram_story_model import DiagramStoryModel
from cdd_guidance.practices.stories.model.story_map_files import THIN_SLICING_FILES, StoryMapFiles
from cdd_guidance.practices.stories.model.story_model import StoryModel


class PracticeOutsideSession(Exception):
    """Raised when a practice is asked to read files by path but works in no session that names their project."""


class ThinSlicedMap:
    """A story map read with the increments of the thin slice beside it, to be drawn as that thin slice: one lane for
    each increment, holding the stories it delivers under their sub-epics. A render of ``thin-slice.md`` to a drawing
    reads this, so the drawing shows the increments rather than the thin slice's headings read as epics."""

    def __init__(self, story_map: StoryModel) -> None:
        self.story_map = story_map

    def semantic_type(self) -> str:
        return "ThinSlice"

    def drawn_by(self, diagram: type[DiagramStoryModel]) -> str:
        """Its increments drawn in the format of diagram, a story model that draws thin slices."""
        return diagram(self.story_map).save_thin_slice()


class StoriesFormats(PracticeFormats):
    """The formats Stories reads and writes. A story test in code carries its epic and sub-epic only in its folders,
    under the story map that names them, so a render from code files reads them as files beside that map, not as one
    run of text; and the TypeScript format is made with the folder of the step library its story tests import."""

    @property
    def adapter_settings(self) -> dict[str, Any]:
        """The folder tests are written under, and the step library folder a pattern names for the TypeScript format."""
        return {**super().adapter_settings, "story_test_folder": self._practice.story_test_folder}

    def read(self, paths: list[str] | str, request: RenderRequest) -> Any:
        """The story map in the files at paths when they are code: the story tests, merged onto the story maps beside
        them. Paths and node paths are named from the project, as every path in a session is."""
        named = [Path(entry) for entry in ([paths] if isinstance(paths, str) else paths)]
        if not request.source_format.is_code:
            return self._thin_sliced_map(named, request) or super().read(paths, request)
        project = self._project_of(named)
        entries = [project / entry for entry in named]
        files = [found for entry in entries for found in (sorted(entry.rglob("*")) if entry.is_dir() else [entry])]
        return self._practice.read_files([path for path in files if path.is_file()], project)

    def render(self, request: RenderRequest) -> dict:
        """What request renders to; a thin slice read for a drawing is drawn as its increments' lanes."""
        if isinstance(request.content, ThinSlicedMap):
            return {"format": request.format, "content": request.content.drawn_by(self.adapter_class(request.format))}
        return super().render(request)

    def _thin_sliced_map(self, named: list[Path], request: RenderRequest) -> ThinSlicedMap | None:
        """The markdown story map beside the thin slice named alone, with that thin slice's increments, when the
        render is to a format that draws thin slices; none for any other files or format, or with no story map
        beside it."""
        draws = request.format in self and issubclass(self.adapter_class(request.format), DiagramStoryModel)
        if not draws or len(named) != 1 or named[0].name not in THIN_SLICING_FILES:
            return None
        project = self._project_of(named)
        story_map = StoryMapFiles((project / named[0]).parent).nearest()
        if story_map is None or story_map.suffix.lower() != ".md":
            return None
        return ThinSlicedMap(self.adapter_class("markdown")().opened_from(story_map, project))

    def _project_of(self, named: list[Path]) -> Path:
        """The folder paths are named from: the repository of the session the practice works in. The MCP host serves
        every project from its own folder, so a practice in no session, as a script makes one, takes only absolute
        paths and names its files from the folder those paths share."""
        session = self._practice.session
        if session is not None:
            return session.repo_path
        if not named or not all(path.is_absolute() for path in named):
            raise PracticeOutsideSession(
                f"{type(self._practice).__name__} works in no session, so it has no project to read {[str(path) for path in named]} from"
            )
        shared = Path(os.path.commonpath([str(path) for path in named]))
        return shared if shared.is_dir() else shared.parent
