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
                "sketch": ("practices.stories.model.sketch.sketch_story_model", "SketchStoryModel"),
                "knowledge_graph": (
                    "practices.stories.model.knowledge_graph.nodes",
                    "KnowledgeGraphStoryModel",
                ),
                "markdown": ("stories.model.markdown.nodes", "MarkdownStoryModel"),
                "json": ("stories.model.json.nodes", "JsonStoryModel"),
                "drawio": ("stories.model.drawio.nodes", "DrawIOStoryModel"),
                "miro": ("stories.model.miro.nodes", "MiroStoryModel"),
                "python": ("stories.model.python.python_story_model", "PythonStoryModel"),
                "typescript": ("stories.model.typescript.typescript_story_model", "TypeScriptStoryModel"),
                "java": ("stories.model.java.java_story_model", "JavaStoryModel"),
                "javascript": ("stories.model.javascript.javascript_story_model", "JavaScriptStoryModel"),
            },
        )
        if stage is not None:
            self._activate(stage=stage)
