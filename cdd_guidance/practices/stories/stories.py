"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance

from cdd_guidance.practices.stories.model.desktop_story_test import DesktopStoryTest
from cdd_guidance.practices.stories.model.graph_reading import StoriesReading
from cdd_guidance.practices.stories.model.project_story_files import OnFile, ProjectStoryFiles
from cdd_guidance.practices.stories.model.sketch.sketch_story_model import SketchStoryModel
from cdd_guidance.practices.stories.model.story_map_files import STORY_TESTS_FOLDER
from cdd_guidance.practices.stories.model.story_model import StoryNode
from cdd_guidance.practices.stories.stories_formats import StoriesFormats

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

    def story_files(self, project: Path, on_file: OnFile = None) -> ProjectStoryFiles:
        """The story maps and story tests of project as this practice reads them, each node naming its file as a path
        from project; on_file hears each file a read takes."""
        return ProjectStoryFiles(self.formats, project, on_file)

    def story_tests(self, project: Path) -> dict[str, list[str]]:
        """Each story test its fidelities declare in the session it works in, by its path from project, with the names
        of the stories it holds: the acceptance tests a story map links each story to."""
        outputs = [fidelity.session_output for fidelity in self.fidelities if fidelity.session_output is not None]
        return self.story_files(project).story_tests([file for output in outputs for file in output.written.every_file()])

    @staticmethod
    def desktop_story_tests(project: Path) -> list[DesktopStoryTest]:
        """Each story of every desktop story test under project's story_tests folder: its file, its scenarios, and
        each step with the lines the file holds below it, which a walk in the Claude desktop app follows."""
        return DesktopStoryTest.every_one_in(Path(project))

StoryNode.practice_class = Stories
