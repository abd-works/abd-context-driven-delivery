"""A whiteboard file in a project, read for a page that draws it: the one reader of a ``.whiteboard`` file, so no page
reads the file's records again in its own language."""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.data_class import data_field, identity, language_adapter
from harness.mcp.mcp_annotations import mcp

from .whiteboard import Whiteboard


@identity("path")
@language_adapter(language="typescript")
@agent_toolset
class WhiteboardFile:
    """Answer the board a ``.whiteboard`` file in the project holds, its elements as data, so a page such as the Files
    app draws it from the generated ``WhiteboardData`` and never reads the file's records itself."""

    def __init__(self, path: str, board: Whiteboard) -> None:
        self._path = path
        self._board = board

    @classmethod
    @tool_subject
    def load(cls, path: str, *, project: Path | str) -> WhiteboardFile:
        """The whiteboard file at path, from project, the folder the call names; text that is no saved board raises
        *UnreadableBoard*, saying why."""
        return cls(path, Whiteboard.from_text((Path(project) / path).read_text(encoding="utf-8")))

    @mcp
    @agent_tool
    @noSessionLog
    def show(self) -> WhiteboardFile:
        """Return the board the file holds: its title, and its sections, shapes, labels and arrows, each whole and with
        its place on the board."""
        return self

    @property
    @data_field
    def path(self) -> str:
        """The file, as a path from the project."""
        return self._path

    @property
    @data_field
    def board(self) -> Whiteboard:
        return self._board
