"""A guidance's own instructions tool: the whole guidance a practice, a fidelity, or a pattern gives when called."""
from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import AgentInstructions

if TYPE_CHECKING:
    from harness.agent_tools.tool_call import ToolCall

# What the MCP tool list says after the opening paragraph of a guidance's instructions, whose call returns the rest.
LISTED_INSTRUCTIONS_NOTE = "Call this tool for the full instructions."


@dataclass
class GuidanceInstructions(AgentInstructions):
    """The ``instructions`` member of a guidance, published as its own tool: a call answers the guidance's whole
    instructions, described by its overview when its docstring says nothing. Every chat carries the MCP tool list each
    turn the tool is loaded, so the list gives only the overview's opening paragraph; the file installed for it carries
    the guidance's schema."""

    @functools.cached_property
    def listed_description(self) -> str:
        """The opening paragraph of its description, and a note that a call returns the rest; its one paragraph alone
        when it has only one."""
        paragraphs = [part.strip() for part in self.description.split("\n\n") if part.strip()]
        prose = [part for part in paragraphs if not part.startswith("#")]
        if len(prose) <= 1:
            return "\n\n".join(prose) or self.description
        return f"{prose[0]}\n\n{LISTED_INSTRUCTIONS_NOTE}"

    @functools.cached_property
    def description(self) -> str:
        """Its docstring, expanded, else the guidance's overview."""
        expanded = self.toolset.class_markdown.expand_docstring(self.docstring)
        if expanded:
            return expanded
        overview = (self.toolset.overview or "").strip()
        return overview or self.docstring or self.callable.__name__

    @property
    def served_body(self) -> str:
        """What the installed file says above the call: its own body, then the guidance's schema guide when the body
        does not already hold it."""
        own = super().served_body
        schema = self.toolset.schema_guide().strip()
        return "\n\n".join(part for part in (own, schema if schema not in own else "") if part)

    def answer(self, call: ToolCall) -> str:
        """The guidance's whole instructions, read on the guidance made for call."""
        tool = self._on(self.toolset.for_call(call))
        tool.log_session_invocation(call)
        return tool.toolset.instructions
