"""Module: space/session. Model delta (clean-engineering-model, python): *FidelitySessionOutput*.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#fidelitysessionoutput-extended
Deleted: kept_format, keep_format."""
from __future__ import annotations

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.guidance.guidance import FidelityGuidance
from harness.installation.data_class import data_field, language_adapter
from harness.mcp.mcp_server import mcp


class FormatNotOffered(ValueError):
    def __init__(self, fidelity: FidelityGuidance, format: str) -> None:
        self.fidelity = fidelity
        self.format = format


@language_adapter(language="typescript")
@agent_toolset
class FidelitySessionOutput:
    # chosen_formats only ever holds formats the fidelity offers, each once

    @classmethod
    @tool_subject
    def load(cls, session: str, practice: str, fidelity: str, *, call: ToolCall) -> FidelitySessionOutput:
        ...

    @property
    @data_field
    def chosen_formats(self) -> list[str]:
        ...

    @mcp
    @agent_tool
    def choose_format(self, format: str, is_chosen: bool) -> FidelitySessionOutput:
        # raises FormatNotOffered for a format the fidelity does not offer
        # -> self.chosen_formats
        ...


class PracticeSessionOutput:
    @property
    @data_field
    def design_view(self) -> str:
        # the Claude Design link of the latest design canvas version under this practice's output root; empty while off
        # -> CanvasVersions.in_practice_root(self.output_root).link(latest)
        ...
