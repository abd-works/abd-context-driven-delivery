"""{ClassName} practice guidance."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class {ClassName}(PracticeGuidance):
    """# Instructions"""

    def __init__(
        self,
        fidelity: str = "{default_fidelity}",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        super().__init__(
            format=format,
            fidelity=fidelity,
            default_workspace_folder=".",
            # formats={{
            #     "markdown": ("{domain_slug}.model.markdown.nodes", "MarkdownModel"),
            # }},
        )
        if path is not None or session is not None:
            self._attach_workspace(path=path, session=session)
