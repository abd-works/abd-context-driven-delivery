# @toolset-manifest python -m tools manifest context_tools.base.create_context_tool.create_context_tool:CreateContextTool
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate
"""CreateContextTool — scaffold new @base_context_tool domains under context_tools/."""

from __future__ import annotations

from context_tools import base_context_tool


@base_context_tool
class CreateContextTool:
    """§ Instructions"""

    default_workspace_folder: str = "."
    context_index_key: str = "create_context_tool"

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__(format=format, path=path, session=session, workspace=workspace)
