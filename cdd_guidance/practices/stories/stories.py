"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance
from harness.markdown.format import Format


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

    # Step library folder for the TypeScript render; a pattern names it. None keeps story-test.ts at the tests root.
    story_test_folder: str | None = None

    def __init__(
        self,
        fidelity: str = "story_map",
        format: str | None = None,
        stage: str | None = None,
    ) -> None:
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

    def read_paths(self, paths: list[str] | str, source: str | None = None):
        """Story tests in code carry their epic and sub-epic only in their folders, under the story map that names them,
        so they are read as files beside that map, not as one run of text. Paths and node paths are named from the
        project, as every path in a session is."""
        if not Format(source or self.format).is_code:
            return super().read_paths(paths, source)
        from cdd_guidance.practices.stories.model.story_model import StoryModel

        project = self.project_folder
        entries = [project / entry for entry in ([paths] if isinstance(paths, str) else paths)]
        files = [found for entry in entries for found in (sorted(entry.rglob("*")) if entry.is_dir() else [entry])]
        return StoryModel.load_files([path for path in files if path.is_file()], project)

    @property
    def project_folder(self) -> Path:
        """The project the session this practice works in names its paths from: the session's repository. A practice
        made outside any session, as a script makes one, names its paths from the current folder."""
        return Path(getattr(self.workspace, "repo_path", None) or Path.cwd())

    def _live_adapter(self, format_name: str):
        if self.story_test_folder is None or Format(format_name).name != "typescript":
            return super()._live_adapter(format_name)
        return self._format_adapter(format_name)(
            tests_root=self.default_workspace_folder,
            story_test_folder=self.story_test_folder,
        )
