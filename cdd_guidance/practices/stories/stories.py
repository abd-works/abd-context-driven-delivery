"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

from cdd_guidance.practices.stories.model.graph_reading import StoriesReading
from cdd_guidance.practices.stories.model.sketch.sketch_story_model import SketchStoryModel
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles, is_story_map_file
from cdd_guidance.practices.stories.model.story_model import StoryNode
from cdd_guidance.practices.stories.stories_formats import StoriesFormats


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

    def __init__(
        self,
        fidelity: str = "story_map",
        format: str | None = None,
        story_test_folder: str | None = None,
    ) -> None:
        # Step library folder for the TypeScript render; a pattern names it. None keeps story-test.ts at the tests root.
        self.story_test_folder = story_test_folder
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder="tests",
            formats={
                "sketch": ("cdd_guidance.practices.stories.model.sketch.sketch_story_model", "SketchStoryModel"),
                "markdown": ("cdd_guidance.practices.stories.model.markdown.nodes", "MarkdownStoryModel"),
                "json": ("cdd_guidance.practices.stories.model.json.nodes", "JsonStoryModel"),
                "drawio": ("cdd_guidance.practices.stories.model.drawio.nodes", "DrawIOStoryModel"),
                "miro": ("cdd_guidance.practices.stories.model.miro.nodes", "MiroStoryModel"),
                "python": ("cdd_guidance.practices.stories.model.python.python_story_model", "PythonStoryModel"),
                "typescript": ("cdd_guidance.practices.stories.model.typescript.typescript_story_model", "TypeScriptStoryModel"),
                "java": ("cdd_guidance.practices.stories.model.java.java_story_model", "JavaStoryModel"),
                "javascript": ("cdd_guidance.practices.stories.model.javascript.javascript_story_model", "JavaScriptStoryModel"),
            },
        )

    ## reading story maps and story tests from files

    def read_folder(self, root: Path, *, on_file=None):
        """The story map in the folder root: the nearest story map at or above it, else its story-graph.json, else the
        markdown story maps under it, with their scenarios and increments."""
        from cdd_guidance.practices.stories.model.story_model import StoryModel

        files = StoryMapFiles(root)
        nearest = files.nearest()
        if nearest is not None:
            return self._story_map_file(nearest, nearest.parent, on_file)
        return (
            self.formats.adapter_class("json").from_workspace(files.folder)
            or self.formats.adapter_class("markdown").from_workspace(files.folder, on_file=on_file)
            or StoryModel()
        )

    def read_files(self, files: list[Path], project: Path, *, on_file=None):
        """The story maps and story tests among files, merged into one story map whose nodes name their files as paths
        from project. A story test holds one Story's scenarios in its own language, and the story map says which epic
        that Story sits under, so a story test's scenarios go on the map's Story of the same name, and a story test
        with no map listed reads the map in its own folder or the nearest one above it."""
        from cdd_guidance.practices.stories.model.story_map_files import path_from
        from cdd_guidance.practices.stories.model.story_model import StoryModel

        project = Path(project).resolve()
        paths = [Path(item).resolve() for item in files]
        tests = [path for path in paths if self._story_test_reader(path) is not None]
        maps = [path for path in paths if is_story_map_file(path)]
        maps += [found for found in self._maps_beside(tests, project) if found not in maps]
        merged = StoryModel()
        for path in maps:
            read = self._story_map_file(path, project, on_file)
            merged.source_texts.update(read.source_texts)
            for epic in list(read.epics):
                merged.append_epic(epic)
        for path in tests:
            file = path_from(project, path)
            if on_file is not None:
                on_file(file)
            text = path.read_text(encoding="utf-8")
            merged.source_texts.update(_texts_of_story_test(file, text, project))
            merged.take_scenarios(self._story_test_reader(path).story_type.load_all(text), file)
        return merged

    def _story_test_reader(self, path: Path):
        """The code format whose story type reads the story test at path; none for any other file."""
        from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel

        adapters = (self.formats.adapter_class(name) for name in self.formats)
        return next((adapter for adapter in adapters if issubclass(adapter, CodeStoryModel) and adapter.is_story_file(path)), None)

    def _story_map_file(self, path: Path, project: Path, on_file=None):
        """The story map in the file at path, read by the format that reads its extension."""
        from cdd_guidance.practices.stories.model.story_model import StoryModel

        return self.formats.for_file(path).from_workspace(path, on_file=on_file, project=project) or StoryModel()

    def _maps_beside(self, tests: list[Path], project: Path) -> list[Path]:
        """The story map each story test belongs to: in its own folder, or the nearest folder above it inside project,
        since story tests sit in epic folders below their map."""
        return list(dict.fromkeys(found for path in tests for found in [StoryMapFiles(path.parent, top=project).nearest()] if found))


def _texts_of_story_test(file: str, text: str, project: Path) -> dict[str, str]:
    """The story test's own text under its path from project, and the text of each examples module it imports by a
    relative import, which an example's facts read its exported names from."""
    from cdd_guidance.practices.stories.model.story_recording import imported_example_files

    texts = {file: text}
    for source in imported_example_files(file, text):
        if (project / source).is_file():
            texts[source] = (project / source).read_text(encoding="utf-8")
    return texts


StoryNode.register_practice(Stories)
