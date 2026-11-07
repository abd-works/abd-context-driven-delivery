"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

import os
from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.markdown.format import Format


class PracticeOutsideSession(Exception):
    """Raised when a practice is asked to read files by path but works in no session that names their project."""


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

    sketch_titles = ("stories:",)
    SHORT_NAME = "Stories"
    COLOUR = "#6BCB77"

    # How the catalog shows this practice; the generator discovers it like the installer does.
    catalog_card = {
        "name": "Stories",
        "label": "stories",
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
        stage: str | None = None,
        story_test_folder: str | None = None,
    ) -> None:
        # Step library folder for the TypeScript render; a pattern names it. None keeps story-test.ts at the tests root.
        self.story_test_folder = story_test_folder
        super().__init__(
            format=format,
            fidelity=None if stage is not None else fidelity,
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
        if stage is not None:
            self._activate(stage=stage)

    # In the knowledge graph: Stories' epics, stories, scenarios, steps, and examples, linked to the Clean Engineering
    # operations each step calls and the classes and properties each example shows.
    source_ordered_types = frozenset({"Background", "Scenario", "Step", "Story"})
    rule_types = {"SubEpic": ("Epic", "StoryNode"), "Epic": ("StoryNode",), "Story": ("StoryNode",)}

    def align_node(self, node) -> None:
        from cdd_guidance.practices.stories.model.graph_reading import align_story_node

        align_story_node(node)

    def read_working_copy(self, practice_graph) -> None:
        """Read the story tests, or the story maps when there are none, into the Stories practice graph."""
        from cdd_guidance.practices.stories.model.graph_reading import read_stories

        read_stories(practice_graph)

    def link_to_other_practices(self, graph) -> None:
        """Link each step to the operations it calls and each example to the classes and properties it shows."""
        from cdd_guidance.practices.stories.model.graph_reading import link_steps_and_examples

        link_steps_and_examples(graph)

    def read_paths(self, paths: list[str] | str, source: str | None = None):
        """Story tests in code carry their epic and sub-epic only in their folders, under the story map that names them,
        so they are read as files beside that map, not as one run of text. Paths and node paths are named from the
        project, as every path in a session is."""
        if not Format(source or self.format).is_code:
            return super().read_paths(paths, source)
        from cdd_guidance.practices.stories.model.story_model import StoryModel

        named = [Path(entry) for entry in ([paths] if isinstance(paths, str) else paths)]
        project = self._project_of(named)
        entries = [project / entry for entry in named]
        files = [found for entry in entries for found in (sorted(entry.rglob("*")) if entry.is_dir() else [entry])]
        return StoryModel.load_files([path for path in files if path.is_file()], project)

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

    def _live_adapter(self, format_name: str):
        if self.story_test_folder is None or Format(format_name).name != "typescript":
            return super()._live_adapter(format_name)
        return self._format_adapter(format_name)(
            tests_root=self.default_workspace_folder,
            story_test_folder=self.story_test_folder,
        )
