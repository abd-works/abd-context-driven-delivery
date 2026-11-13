"""Module: cdd_guidance/practices/stories/model. Model delta (clean-engineering-model, python): story map edits behind the Story UI.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#cdd_guidancepracticesstoriesmodel
Replaces the Story UI's TypeScript StoryMapModel, EpicModel, SubEpicModel, StoryModel, ScenarioModel and
StoryMapRepository (../story-ui/packages/story-map-workspace/stories/stories.ts)."""
from __future__ import annotations

from typing import Annotated

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.graph.graph import Graph
from space.session.practice_session_output import FidelitySessionOutput
from harness.installation.data_class import SourceFile, data_field, language_adapter
from harness.mcp.mcp_server import mcp


class StoryMapEditRefused(Exception):
    def __init__(self, node: StoryNode, operation: str, reason: str) -> None:
        self.node = node
        self.operation = operation
        self.reason = reason


@language_adapter(language="typescript")
@agent_toolset
class StoryNode:
    # every edit saves through its story map before it answers

    @classmethod
    @tool_subject
    def load(cls, node: str, *, call: ToolCall) -> StoryNode:
        # node is `{file}#{path}`
        # -> StoryModel.load(file)
        ...

    @property
    def story_map(self) -> StoryModel:
        ...

    @mcp
    @agent_tool
    def rename(self, name: str) -> StoryModel:
        # -> self.story_map.save
        ...

    @mcp
    @agent_tool
    def move_before(self, other: StoryNode) -> StoryModel:
        # raises StoryMapEditRefused when other is not of its own kind
        # -> self.story_map.save
        ...

    @mcp
    @agent_tool
    def remove(self) -> StoryModel:
        # -> self.story_map.save
        ...


@language_adapter(language="typescript")
@agent_toolset
class StoryModel(StoryNode):
    # a story map opened in a session writes only under the session's roots

    def __init__(self, source: StoryModel | Graph | None = None, graph: Graph | None = None) -> None:
        # -> self.copy_of (when source is a story model), as today
        ...

    @classmethod
    @tool_subject
    def load(cls, file: str, *, call: ToolCall) -> StoryModel:
        # -> call.session.file_manager.read(file)
        # -> call.session.graph.practices.of(Stories).read_files
        # -> StoryModel.file
        ...

    @property
    @data_field
    def file(self) -> Annotated[str, SourceFile]:
        ...

    @property
    @data_field
    def formats(self) -> FidelitySessionOutput:
        # -> self._opened.fidelity.session_output (offered_formats, chosen_formats)
        ...

    @property
    @data_field
    def refusal(self) -> str:
        # -> self._opened.refusal
        ...

    @classmethod
    @mcp
    @agent_tool
    def open_in_session(cls, *, call: ToolCall) -> StoryModel:
        # the first story map file the open session's Stories practice declares
        ...

    @mcp
    @agent_tool
    def show(self) -> StoryModel:
        ...

    @mcp
    @agent_tool
    def new_epic(self, name: str) -> StoryModel:
        # -> self.append_epic
        # -> self.save
        ...

    def save(self) -> StoryModel:
        # its own file first, then each chosen format; refused while self.refusal says why
        # -> self._opened.write (OpenedStoryMap: Stories.formats.render, session.graph.refresh)
        ...


class Epic(StoryNode):
    @mcp
    @agent_tool
    def new_epic(self, name: str) -> StoryModel:
        # -> self.append_epic
        # -> self.story_map.save
        ...

    @mcp
    @agent_tool
    def new_story(self, name: str) -> StoryModel:
        # -> self.append_story
        # -> self.story_map.save
        ...


class Story(StoryNode):
    @mcp
    @agent_tool
    def new_scenario(self, name: str) -> StoryModel:
        # -> self.story_map.save
        ...


class Scenario(StoryNode):
    @mcp
    @agent_tool
    def new_step(self, step_type: str, text: str) -> StoryModel:
        # -> self.story_map.save
        ...


class Step(StoryNode):
    @mcp
    @agent_tool
    def edit_text(self, text: str) -> StoryModel:
        # -> self.story_map.save
        ...
