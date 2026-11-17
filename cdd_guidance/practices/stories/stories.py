"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Optional

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

from cdd_guidance.practices.stories.model.graph_reading import StoriesReading
from cdd_guidance.practices.stories.model.sketch.sketch_story_model import SketchStoryModel
from cdd_guidance.practices.stories.model.story_map_files import (
    STORY_FILE_SUFFIXES,
    STORY_TESTS_FOLDER,
    StoryMapFiles,
    is_story_map_file,
    path_from,
    preferred_maps,
)
from cdd_guidance.practices.stories.model.story_model import StoryModel, StoryNode
from cdd_guidance.practices.stories.model.story_recording import StorySource, StorySources
from cdd_guidance.practices.stories.stories_formats import StoriesFormats

# A story test names its story map: `# Map: ../../.context/story-map.md#story` or `Map: .context/story-map.md.`
_MAP_LINE = re.compile(r"Map:\s*(\S+?\.md)\b")
# Hears each file a read takes, by its path from the project, as it is read.
OnFile = Optional[Callable[[str], None]]
# Each format Stories writes, and the module and class of the story model that reads and writes it.
_FORMAT_ADAPTERS = {
    "sketch": ("cdd_guidance.practices.stories.model.sketch.sketch_story_model", "SketchStoryModel"),
    "markdown": ("cdd_guidance.practices.stories.model.markdown.nodes", "MarkdownStoryModel"),
    "json": ("cdd_guidance.practices.stories.model.json.nodes", "JsonStoryModel"),
    "drawio": ("cdd_guidance.practices.stories.model.drawio.nodes", "DrawIOStoryModel"),
    "miro": ("cdd_guidance.practices.stories.model.miro.nodes", "MiroStoryModel"),
    "whiteboard": ("cdd_guidance.practices.stories.model.whiteboard.nodes", "WhiteboardStoryModel"),
    "python": ("cdd_guidance.practices.stories.model.python.python_story_model", "PythonStoryModel"),
    "typescript": ("cdd_guidance.practices.stories.model.typescript.typescript_story_model", "TypeScriptStoryModel"),
    "java": ("cdd_guidance.practices.stories.model.java.java_story_model", "JavaStoryModel"),
    "javascript": ("cdd_guidance.practices.stories.model.javascript.javascript_story_model", "JavaScriptStoryModel"),
}


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchStoryModel.lens
    # Its story tests in code are read as files beside the story map that names them; and it takes part in the graph
    # through its story tests, or its story maps when there are none.
    formats_type = StoriesFormats
    reading_type = StoriesReading
    SHORT_NAME = "Stories"
    COLOUR = "#6BCB77"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Stories",
        "label": "stories",
        # The approach page's stage examples are Stories' artifacts.
        "stage_examples": True,
        "family": "aad-fam-sdd",
        "perspective": "sdd",
        "order": 10,
        "blurb": "Map user interactions to system behaviors, then define each through executable specifications.",
        "spec_blurb": "Executable scenario-specifications with real-world examples",
    }

    first_fidelity = "story_map"

    def __init__(
        self,
        fidelity: str | None = "",
        format: str | None = None,
        story_test_folder: str | None = None,
    ) -> None:
        # Step library folder for the TypeScript render; a pattern names it. None keeps story-test.ts at the tests root.
        self.story_test_folder = story_test_folder
        super().__init__(format=format, fidelity=fidelity)

    default_workspace_folder = "tests"
    format_adapters = _FORMAT_ADAPTERS

    ## reading story maps and story tests from files

    def read_folder(self, root: Path, *, on_file: OnFile = None) -> StoryModel:
        """The story map in the folder root: the nearest story map at or above it, else its story-graph.json, else the
        markdown story maps under it, with their scenarios and increments. A map under root names its files from root,
        as a read of the files being edited names them, so the two reads place each node in the same file; a map above
        root names them from its own folder."""
        files = StoryMapFiles(root)
        nearest = files.nearest()
        if nearest is not None:
            inside = Path(root).resolve() in nearest.resolve().parents
            return self._story_map_file(nearest, Path(root) if inside else nearest.parent, on_file)
        return (
            self.formats.adapter_class("json").from_workspace(files.folder)
            or self.formats.adapter_class("markdown").from_workspace(files.folder, on_file=on_file)
            or StoryModel()
        )

    def read_files(self, files: list[Path], project: Path, *, on_file: OnFile = None) -> StoryModel:
        """The story maps and story tests among files, merged into one story map whose nodes name their files as paths
        from project. Story tests in code under a project's story_tests are the map themselves (``_story_map_of_code``);
        otherwise the maps among files and beside them are read (``_maps_to_read``), and a story test's scenarios go on
        the map's Story of the same name, which it specifies."""
        project = Path(project).resolve()
        paths = [Path(item).resolve() for item in files]
        tests = [path for path in paths if self._story_test_reader(path) is not None]
        from_code = self._story_map_of_code(tests, project, on_file)
        if from_code.epics:
            return from_code
        merged = StoryModel()
        for path in self._maps_to_read(paths, tests, project):
            self._take_map(merged, self._story_map_file(path, project, on_file))
        for path in tests:
            self._take_story_test(merged, self._read_story_test(path, project, on_file), project)
        return merged

    def _maps_to_read(self, paths: list[Path], tests: list[Path], project: Path) -> list[Path]:
        """The story maps among paths, and the map beside each story test and scenarios markdown file among them, which
        reads that file's scenarios as they are now: one file per map, its markdown before its drawio
        (``preferred_maps``)."""
        maps = [path for path in paths if is_story_map_file(path)]
        scenario_files = [path for path in paths if path.suffix.lower() == ".md" and path.name.endswith(STORY_FILE_SUFFIXES)]
        return preferred_maps(maps + [found for found in self._maps_beside(tests + scenario_files, project) if found not in maps])

    def _take_map(self, merged: StoryModel, read: StoryModel) -> None:
        merged.sources.take(read.sources)
        for epic in list(read.epics):
            merged.epics.append(epic)

    def _read_story_test(self, path: Path, project: Path, on_file: OnFile) -> StorySource:
        file = path_from(project, path)
        if on_file is not None:
            on_file(file)
        return StorySource(file, path.read_text(encoding="utf-8"))

    def _take_story_test(self, merged: StoryModel, test: StorySource, project: Path) -> None:
        """The story test's scenarios onto merged's Story of the same name, and its text and its examples modules'."""
        merged.sources.take(self._story_test_sources(test, project))
        reader = self._story_test_reader(project / test.file)
        merged.test_scenarios.take(reader.story_type.load_file(test.text, project), test.file)

    def open_file(self, path: Path, project: Path):
        """The story map an edit to the Stories file at path writes back: a markdown story map or scenarios file read
        by itself (``MarkdownStoryModel.opened_from``), so a save keeps every line it does not change; a story map in
        another format read by the format that reads its extension; a story test, which is read and not edited, merged
        onto its story map (``read_files``)."""
        from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel

        if self._story_test_reader(Path(path)) is not None:
            return self.read_files([path], project)
        adapter = self.formats.for_file(Path(path))
        if isinstance(adapter, MarkdownStoryModel):
            return adapter.opened_from(Path(path), project)
        return adapter.from_workspace(Path(path), project=project) or adapter

    def _story_map_of_code(self, tests: list[Path], project: Path, on_file: OnFile = None) -> StoryModel:
        """The story map the story tests in code among tests hold under the project's story_tests, each language read
        by its own format: their folders are its epics and sub-epics, and their stories and scenarios its own, each
        naming its test as its file. An epic another language already gave is kept from the first. Empty when none sits
        under story_tests."""
        merged = StoryModel()
        for reader, texts in self._texts_by_reader(tests, project).items():
            read = type(reader)(tests_root=STORY_TESTS_FOLDER).parse(texts, on_file=on_file, project=project)
            merged.sources.take(read.sources)
            held = {epic.name for epic in merged.epics}
            for epic in [epic for epic in read.epics if epic.name not in held]:
                merged.epics.append(epic)
        return merged

    def _texts_by_reader(self, tests: list[Path], project: Path) -> dict[type, dict[str, str]]:
        """Each story test's text by its path from project, grouped by the code format that reads it."""
        by_reader: dict[type, dict[str, str]] = {}
        for path in tests:
            by_reader.setdefault(self._story_test_reader(path), {})[path_from(project, path)] = path.read_text(encoding="utf-8")
        return by_reader

    def story_tests(self, project: Path) -> dict[str, list[str]]:
        """Each story test its fidelities declare in the session it works in, by its path from project, with the names
        of the stories it holds: the acceptance tests a story map links each story to."""
        project = Path(project).resolve()
        outputs = [fidelity.session_output for fidelity in self.fidelities if fidelity.session_output is not None]
        held = {}
        for path in sorted({file.resolve() for output in outputs for file in output.written.every_file()}):
            reader = self._story_test_reader(path)
            if reader is not None:
                held[path_from(project, path)] = [story.name for story in reader.story_type.load_file(path.read_text(encoding="utf-8"), project)]
        return held

    def _story_test_reader(self, path: Path):
        """The code format whose story type reads the story test at path; none for any other file."""
        from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel

        adapters = (self.formats.adapter(name) for name in self.formats)
        return next((adapter for adapter in adapters if isinstance(adapter, CodeStoryModel) and adapter.is_story_file(path)), None)

    def _story_map_file(self, path: Path, project: Path, on_file: OnFile = None) -> StoryModel:
        """The story map in the file at path, read by the format that reads its extension."""
        return self.formats.for_file(path).from_workspace(path, on_file=on_file, project=project) or StoryModel()

    def _maps_beside(self, tests: list[Path], project: Path) -> list[Path]:
        """The story map each story test belongs to: in its own folder, or the nearest folder above it inside project,
        since story tests sit in epic folders below their map; else the map its text names on a ``Map:`` line, from its
        own folder or from project, for a story test that sits beside the code rather than under its map."""
        found = [StoryMapFiles(path.parent, top=project).nearest() or self._named_map(path, project) for path in tests]
        return list(dict.fromkeys(path for path in found if path))

    def _named_map(self, test: Path, project: Path) -> Path | None:
        """The story map the story test at test names on a ``Map:`` line, from its own folder or from project; none when
        it names none that is there."""
        named = _MAP_LINE.search(test.read_text(encoding="utf-8"))
        if named is None:
            return None
        relative = named.group(1).split("#", 1)[0]
        return next((path for path in (test.parent / relative, project / relative) if path.is_file()), None)

    def _story_test_sources(self, test: StorySource, project: Path) -> StorySources:
        """The story test, and each examples module it imports that is there under project, which an example's facts
        read its exported names from."""
        sources = StorySources()
        sources.add(test.file, test.text)
        for module in test.imported_example_files():
            if (project / module).is_file():
                sources.add(module, (project / module).read_text(encoding="utf-8"))
        return sources


StoryNode.practice_class = Stories
