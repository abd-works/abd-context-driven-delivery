"""Stories' formats: story tests in code are read as files beside the story map that names them."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from harness.guidance.practice_formats import PracticeFormats, Rendered, RenderRequest


from cdd_guidance.practices.stories.model.diagram_story_model import DiagramStoryModel
from cdd_guidance.practices.stories.model.story_map_files import STORY_FILE_SUFFIXES, STORY_TESTS_FOLDER, THIN_SLICING_FILES, StoryMapFiles, path_from
from cdd_guidance.practices.stories.model.story_model import Epic, Scenario, Story, StoryModel


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
        return diagram().copy_of(self.story_map).save_thin_slice()


class SpecifiedStories:
    """The stories the files a render names specify: a story one of them holds, or holds a scenario of. A story map
    read with those files keeps only these, under the epics and sub-epics the map gives them, so a render of one file writes
    that file's stories and none of the rest of the map."""

    def __init__(self, files: list[Path], project: Path) -> None:
        self._files = {path_from(project, file) for file in files}

    def kept_in(self, story_map: StoryModel) -> StoryModel:
        """story_map, holding only the stories the files specify and the epics above them."""
        story_map.epics.refill([epic for epic in story_map.epics if self._keeps(epic)])
        return story_map

    def _keeps(self, epic: Epic) -> bool:
        """Whether epic holds a story the files specify, once the stories and sub-epics that hold none are dropped."""
        epic.stories = [story for story in epic.stories if any(self._is_read_from_files(node) for node in (story, *story.scenarios))]
        epic.epics = [sub for sub in epic.epics if self._keeps(sub)]
        return bool(epic.stories or epic.epics)

    def _is_read_from_files(self, node: Story | Scenario) -> bool:
        return node.source is not None and node.source.file in self._files


class ScenariosOnTheirMap:
    """The scenarios markdown files a render names, read on the story map above them: each story the files specify sits
    under the epic and sub-epic the map gives it, so the code written from them is named for those, and the stories
    of the map the files say nothing of are left out."""

    def __init__(self, map_file: Path, files: list[Path], project: Path) -> None:
        self._map_file = map_file
        self._project = project
        self._specified = SpecifiedStories(files, project)

    def read_by(self, markdown: StoryModel) -> StoryModel | None:
        """The map as markdown, the markdown story format, reads it with its scenarios, holding only the stories the
        files specify; none when the map holds none of them."""
        kept = self._specified.kept_in(markdown.read_file(self._map_file, self._project))
        return kept if kept.epics else None


class StoriesFormats(PracticeFormats):
    """The formats Stories reads and writes. A story test in code carries its epic and sub-epic only in its folders,
    under the story map that names them, so a render from code files reads them as files beside that map, not as one
    run of text; and the TypeScript format is made with the folder of the step library its story tests import."""

    @property
    def adapter_settings(self) -> dict[str, Any]:
        """The folder story tests are written under, the project's story_tests, where the scenarios and acceptance
        tests fidelities declare them, and the step library folder a pattern names for the script formats."""
        return {**super().adapter_settings, "tests_root": STORY_TESTS_FOLDER, "story_test_folder": self._practice.story_test_folder}

    def read(self, paths: list[str] | str, request: RenderRequest) -> Any:
        """The story map in the files at paths when they are code: the story tests, merged onto the story maps beside
        them. Paths and node paths are named from the project, as every path in a session is."""
        named = [Path(entry) for entry in ([paths] if isinstance(paths, str) else paths)]
        if not request.source_format.is_code:
            return self._thin_sliced_map(named, request) or self._scenarios_on_their_map(named, request) or super().read(paths, request)
        project = self._project_of(named)
        entries = [project / entry for entry in named]
        files = [path for entry in entries for path in (sorted(entry.rglob("*")) if entry.is_dir() else [entry]) if path.is_file()]
        return SpecifiedStories(files, project).kept_in(self._practice.story_files(project).story_map_of(files))

    def render(self, request: RenderRequest) -> Rendered:
        """What request renders to; a thin slice read for a drawing is drawn as its increments' lanes, and story
        tests in code rendered to markdown, at a fidelity that declares a scenarios file for each story, are
        written as those files, each by the path the fidelity declares for it."""
        if isinstance(request.content, ThinSlicedMap):
            return Rendered(request.format, request.content.drawn_by(self.adapter_class(request.format)))
        if self._writes_scenarios_files(request):
            markdown = self.adapter(request.format).copy_of(self._object_model(request.content, request.source_format))
            return Rendered(request.format, markdown.scenarios_files(STORY_TESTS_FOLDER))
        return super().render(request)

    def _writes_scenarios_files(self, request: RenderRequest) -> bool:
        """Whether request renders story tests in code to the scenarios files of their stories: a render from code to
        markdown, at a fidelity whose markdown paths name a story's own scenarios file."""
        if request.format != "markdown" or not request.source_format.is_code or request.fidelity is None:
            return False
        declared = request.fidelity.declared.outputs.get("markdown", [])
        return any(str(path).endswith(STORY_FILE_SUFFIXES) for path in ([declared] if isinstance(declared, str) else declared))

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

    def _scenarios_on_their_map(self, named: list[Path], request: RenderRequest) -> StoryModel | None:
        """The stories the scenarios markdown files at named specify, on the story map above them, for a render to
        code, which names each story test for its epic and sub-epic; none for a render to any other format, for files
        that are not all scenarios files, or with no markdown story map above them that holds their stories."""
        if not request.format.is_code:
            return None
        project = self._project_of(named)
        entries = [project / entry for entry in named]
        files = [found for entry in entries for found in (sorted(entry.rglob("*.md")) if entry.is_dir() else [entry])]
        if not files or not all(file.name.endswith(STORY_FILE_SUFFIXES) and file.suffix.lower() == ".md" for file in files):
            return None
        story_map = StoryMapFiles(files[0].parent, top=project).nearest()
        if story_map is None or story_map.suffix.lower() != ".md":
            return None
        return ScenariosOnTheirMap(story_map, files, project).read_by(self.adapter("markdown"))

    def _project_of(self, named: list[Path]) -> Path:
        """The folder paths are named from: the repository of the session the practice works in. The MCP host serves
        every project from its own folder, so a practice in no session, as a script makes one, takes only absolute
        paths and names its files from the folder those paths share."""
        session = self._practice.session
        if session is not None:
            return session.checkout.root
        if not named or not all(path.is_absolute() for path in named):
            raise PracticeOutsideSession(
                f"{type(self._practice).__name__} works in no session, so it has no project to read {[str(path) for path in named]} from"
            )
        shared = Path(os.path.commonpath([str(path) for path in named]))
        return shared if shared.is_dir() else shared.parent
