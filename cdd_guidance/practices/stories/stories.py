"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from harness.agent_tools.agent_tools import agent_toolset
from harness.annotations.name import Name
from harness.guidance.guidance import PracticeGuidance
from harness.installation.context_config import CONTEXT_FOLDER

from cdd_guidance.practices.stories.model.graph_reading import StoriesReading
from cdd_guidance.practices.stories.model.project_story_files import OnFile, ProjectStoryFiles
from cdd_guidance.practices.stories.model.sketch.sketch_story_map import SketchStoryMap
from cdd_guidance.practices.stories.model.story_map_files import STORY_TESTS_FOLDER
from cdd_guidance.practices.stories.model.story_map import StoryNode
from cdd_guidance.practices.stories.stories_formats import StoriesFormats

# Each format Stories writes, and the module and class of the story model that reads and writes it.
_FORMAT_ADAPTERS = {
    "sketch": ("cdd_guidance.practices.stories.model.sketch.sketch_story_map", "SketchStoryMap"),
    "markdown": ("cdd_guidance.practices.stories.model.markdown.nodes", "MarkdownStoryMap"),
    "json": ("cdd_guidance.practices.stories.model.json.nodes", "JsonStoryMap"),
    "drawio": ("cdd_guidance.practices.stories.model.drawio.nodes", "DrawIOStoryMap"),
    "miro": ("cdd_guidance.practices.stories.model.miro.nodes", "MiroStoryMap"),
    "whiteboard": ("cdd_guidance.practices.stories.model.whiteboard.nodes", "WhiteboardStoryMap"),
    "python": ("cdd_guidance.practices.stories.model.python.python_story_map", "PythonStoryMap"),
    "typescript": ("cdd_guidance.practices.stories.model.typescript.typescript_story_map", "TypeScriptStoryMap"),
    "javascript": ("cdd_guidance.practices.stories.model.javascript.javascript_story_map", "JavaScriptStoryMap"),
}


@dataclass(frozen=True)
class StoryExampleFiles:
    """Which files of its folders Stories reads at one fidelity (kebab case; empty at none). A story map's examples
    are its story map files alone: the scenario and thin-slice examples, and every other markdown file, are the later
    fidelities'. Read at the story map or at no fidelity, the examples leave out the whole-map examples (thin slices,
    scenario files, and an ``examples`` index), which would show more of a map than a first cut writes."""

    fidelity: str

    def __call__(self, label: str, path: Path) -> bool:
        stem = Name(path.stem).kebab
        whole_map_example = "thin-slice" in stem or stem.startswith("scenario-") or stem == "examples"
        if label == "examples" and self.fidelity in {"story-map", ""} and whole_map_example:
            return False
        if self.fidelity != "story-map":
            return True
        if "scenario" in stem or stem == "thin-slice":
            return False
        return not (path.suffix.lower() == ".md" and "story-map" not in stem and stem != "examples")


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchStoryMap.lens
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

    def reads_file_at(self, fidelity: str | None) -> StoryExampleFiles:
        """The files of its folders it reads at fidelity (``StoryExampleFiles``)."""
        return StoryExampleFiles(Name(fidelity or "").kebab)

    def placed_under(self, declared: PurePosixPath, root: Path) -> Path | None:
        """A declared ``story_tests/...`` path lands under a root inside ``story_tests``, such as one epic's folder,
        below the folders that root already names, and nowhere when the root names a folder deeper than the path goes;
        under a root inside a ``.context`` folder, it lands in the ``story_tests`` beside that ``.context``. Any other
        path lands as any practice's does."""
        if declared.parts[:1] != (STORY_TESTS_FOLDER,):
            return super().placed_under(declared, root)
        if STORY_TESTS_FOLDER in root.parts:
            below = PurePosixPath(*declared.parts[len(root.parts) - root.parts.index(STORY_TESTS_FOLDER) :])
            # An epic's own stories' file is not below a sub-epic's folder: the root already names more folders than it does.
            return root / below if below.parts else None
        if CONTEXT_FOLDER in root.parts:
            return Path(*root.parts[: root.parts.index(CONTEXT_FOLDER)]) / declared
        return root / declared

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

StoryNode.practice_class = Stories
