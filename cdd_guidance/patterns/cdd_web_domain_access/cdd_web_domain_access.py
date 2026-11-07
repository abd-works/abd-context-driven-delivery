"""CDD web domain access - how anything outside Python reaches the CDD domain.
The domain stays in Python. Skills, actions, and commands reach it through MCP tools, and code in any other language
reaches those same tools through the language adapter the installer deploys for it. TypeScript is the first
implementation; see space/kanban/app for the worked example."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class CddWebDomainAccess(PracticeGuidance):
    """How code outside Python reaches the CDD domain: through MCP tools, by a language adapter the installer deploys."""

    pattern = "cdd_web_domain_access"

    def __init__(self) -> None:
        super().__init__(
            format="typescript",
            default_workspace_folder="harness",
        )
