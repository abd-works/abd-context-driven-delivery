"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

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
                "markdown": ("stories.model.markdown.nodes", "MarkdownStoryModel"),
                "json": ("stories.model.json.nodes", "JsonStoryModel"),
                "drawio": ("stories.model.drawio.nodes", "DrawIOStoryModel"),
                "miro": ("stories.model.miro.nodes", "MiroStoryModel"),
                "claude_design": ("stories.model.claude_design.nodes", "ClaudeDesignStoryModel"),
                "python": ("stories.model.python.python_story_model", "PythonStoryModel"),
                "typescript": ("stories.model.typescript.typescript_story_model", "TypeScriptStoryModel"),
                "java": ("stories.model.java.java_story_model", "JavaStoryModel"),
                "javascript": ("stories.model.javascript.javascript_story_model", "JavaScriptStoryModel"),
            },
        )
        if stage is not None:
            self._activate(stage=stage)

    def _live_adapter(self, format_name: str):
        if self.story_test_folder is None or self._canonical_format(format_name) != "typescript":
            return super()._live_adapter(format_name)
        return self._format_adapter(format_name)(
            tests_root=self.default_workspace_folder,
            story_test_folder=self.story_test_folder,
        )
