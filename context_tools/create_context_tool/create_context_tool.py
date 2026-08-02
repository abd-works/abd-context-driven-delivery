# @toolset-manifest python -m tools manifest context_tools.create_context_tool.create_context_tool:CreateContextTool
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""CreateContextTool - scaffold new BaseContextTool domains under context_tools/."""

from __future__ import annotations

from context_tools.base.base_context_tool import BaseContextTool


class CreateContextTool(BaseContextTool):
    """# Instructions"""

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
