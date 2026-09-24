"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

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
                "markdown": ("stories.model.markdown.nodes", "MarkdownStoryMap"),
                "json": ("stories.model.json.nodes", "JsonStoryMap"),
                "drawio": ("stories.model.drawio.nodes", "DrawIOStoryMap"),
                "miro": ("stories.model.miro.nodes", "MiroStoryMap"),
                "python": ("stories.model.python.python_story_map", "PythonStoryMap"),
                "typescript": ("stories.model.typescript.typescript_story_map", "TypeScriptStoryMap"),
                "java": ("stories.model.java.java_story_map", "JavaStoryMap"),
                "javascript": ("stories.model.javascript.javascript_story_map", "JavaScriptStoryMap"),
            },
        )
        if stage is not None:
            self._activate(stage=stage)

    @property
    def model(self):
        from practices.stories.model.transformation.story_map_transformer import (
            StoryMapTransformer,
        )

        class StoriesModel:
            transformer = StoryMapTransformer

        return StoriesModel()
