"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.markdown.format import Format

from cdd_guidance.practices.stories.model.graph_reading import StoriesReading, StoryLinks, align_story_node
from cdd_guidance.practices.stories.model.sketch.sketch_story_model import SketchStoryModel
from cdd_guidance.practices.stories.model.story_map_files import StoryMapFiles, is_story_map_file
from cdd_guidance.practices.stories.model.story_model import StoryNode


class PracticeOutsideSession(Exception):
    """Raised when a practice is asked to read files by path but works in no session that names their project."""


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

    # Its section of a sketch is the one its sketch format reads, held as that one lens.
    sketch_lens = SketchStoryModel.lens
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
        # The story map this practice last wrote onto its graph, whose nodes its links start from.
        self.recorded_map = None
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

    @cached_property
    def typescript_stories(self):
        """The TypeScript format, made once with the folder story tests are written under and the step library
        folder: every TypeScript render and every read of the TypeScript story tests into the graph uses it."""
        return self._format_adapter("typescript")(
            tests_root=self.default_workspace_folder,
            story_test_folder=self.story_test_folder,
        )

    def _live_adapter(self, format_name: str):
        adapter = self._format_adapter(format_name)
        if adapter is type(self.typescript_stories):
            return self.typescript_stories
        return super()._live_adapter(format_name)

    # In the knowledge graph: Stories' epics, stories, scenarios, steps, and examples, linked to the Clean Engineering
    # operations each step calls and the classes and properties each example shows.
    source_ordered_types = frozenset({"Background", "Scenario", "Step", "Story"})
    # A step is recorded as the Given, When, or Then it is, while the schema keeps every step's rules on Step (its
    # given, when, and then types are each a Step), so each carries Step's rules; its check says which kind it judges.
    rule_types = {
        "SubEpic": ("Epic", "StoryNode"),
        "Epic": ("StoryNode",),
        "Story": ("StoryNode",),
        "Given": ("Step",),
        "When": ("Step",),
        "Then": ("Step",),
    }

    @property
    def object_model(self) -> PracticeGuidance | None:
        """The Clean Engineering practice the graph that holds Stories reads beside it, whose operations its steps call
        and whose classes its examples show; none when the graph reads none."""
        from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

        return self.graph.loaded(CleanEngineering) if self.graph is not None else None

    @property
    def domain_model(self) -> PracticeGuidance | None:
        """The DDD practice the graph that holds Stories reads beside it, whose aggregates its scenarios name; none
        when the graph reads none."""
        from cdd_guidance.practices.ddd.ddd import Ddd

        return self.graph.loaded(Ddd) if self.graph is not None else None

    def align_node(self, node) -> None:
        align_story_node(node)

    def read_working_copy(self) -> None:
        """Read the story tests, or the story maps when there are none, and write the story map onto its graph."""
        self.recorded_map = StoriesReading(self).story_map()
        self.graph.report_progress("stories · record")
        self.recorded_map.record(self, on_node=lambda detail: self.graph.report_progress(f"stories · record · {detail}"))

    def link_to_other_practices(self) -> None:
        """Link each step to the operations it calls and each example to the classes and properties it shows."""
        if self.object_model is not None and self.recorded_map is not None:
            StoryLinks(self, self.object_model).link()

    def read_paths(self, paths: list[str] | str, source: str | None = None):
        """Story tests in code carry their epic and sub-epic only in their folders, under the story map that names them,
        so they are read as files beside that map, not as one run of text. Paths and node paths are named from the
        project, as every path in a session is."""
        if not (Format(source).is_code if source else self.format.is_code):
            return super().read_paths(paths, source)
        named = [Path(entry) for entry in ([paths] if isinstance(paths, str) else paths)]
        project = self._project_of(named)
        entries = [project / entry for entry in named]
        files = [found for entry in entries for found in (sorted(entry.rglob("*")) if entry.is_dir() else [entry])]
        return self.read_files([path for path in files if path.is_file()], project)

    def _project_of(self, named: list[Path]) -> Path:
        """The folder paths are named from: the repository of the session this practice works in. The MCP host serves
        every project from its own folder, so a practice in no session, as a script makes one, takes only absolute
        paths and names its files from the folder those paths share."""
        if self.session is not None:
            return self.session.repo_path
        if not named or not all(path.is_absolute() for path in named):
            raise PracticeOutsideSession(
                f"{type(self).__name__} works in no session, so it has no project to read {[str(path) for path in named]} from"
            )
        shared = Path(os.path.commonpath([str(path) for path in named]))
        return shared if shared.is_dir() else shared.parent

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
            self._format_adapter("json").from_workspace(files.folder)
            or self._format_adapter("markdown").from_workspace(files.folder, on_file=on_file)
            or StoryModel()
        )

    def read_files(self, files: list[Path], project: Path, *, on_file=None):
        """The story maps and story tests among files, merged into one story map whose nodes name their files as paths
        from project. A story test holds one Story's scenarios in its own language, and the story map says which epic
        that Story sits under, so a story test's scenarios go on the map's Story of the same name, and a story test
        with no map listed reads the map in its own folder or the nearest one above it."""
        from cdd_guidance.practices.stories.model.source_location import path_from
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

        adapters = (self._format_adapter(name) for name in self.formats)
        return next((adapter for adapter in adapters if issubclass(adapter, CodeStoryModel) and adapter.is_story_file(path)), None)

    def _story_map_file(self, path: Path, project: Path, on_file=None):
        """The story map in the file at path, read by the format that reads its extension."""
        from cdd_guidance.practices.stories.model.story_model import StoryModel

        return self.format_for(path).from_workspace(path, on_file=on_file, project=project) or StoryModel()

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
