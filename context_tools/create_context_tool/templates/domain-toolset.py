# @toolset-manifest python -m tools manifest {module_path}:{ClassName}
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""{ClassName} generator."""

from __future__ import annotations

from primitives.actions.action import agent_instructions  # noqa: F401
from context_tools.base.base_context_tool import BaseContextTool


class {ClassName}(BaseContextTool):
    """# Instructions"""

    # Override when this domain's durable root is not "." (e.g. "tests", "src", "ux").
    default_workspace_folder: str = "."
    # Key in ``{workspace}/.context/context-index.md`` (e.g. "stories").
    context_index_key: str = "{domain_slug}"

    def __init__(
        self,
        format: str = "python",
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__(format=format, path=path, session=session, workspace=workspace)
