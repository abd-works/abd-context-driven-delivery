"""{ClassName} practice guidance."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class {ClassName}(PracticeGuidance):
    """{ClassName}: what this practice brings to the work, in one sentence."""

    first_fidelity = "{default_fidelity}"

    default_workspace_folder = "."
    # format_adapters = {{
    #     "markdown": ("{domain_slug}.model.markdown.nodes", "MarkdownModel"),
    # }}
