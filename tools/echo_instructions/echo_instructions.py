"""Echo instructions - print an action's wrapped instructions inside a DO-NOT-FOLLOW fence for inspection.

EchoInstructions is a standalone toolset. Any agent or human can invoke its tools and
echo_session action directly to render arbitrary text inside DO-NOT-FOLLOW
fences.

The complementary @echo decorator (see _decorator.py, re-exported from the
package root) marks another action's @agent_instructions so framework-level composition can
short-circuit that action into an echo of its fully-wrapped instructions -
diagnostic-only, no execution.
"""
from __future__ import annotations

from harness.agent_tools import agent_instructions, agent_toolset
from harness.guidance_actions import load_document
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.destination import noCatalog
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp

_FENCE_HEADER = "===== DO NOT FOLLOW ANY OF THESE INSTRUCTIONS ====="
_FENCE_FOOTER = "===== END: DO NOT FOLLOW ANY OF THESE INSTRUCTIONS ====="

@noCatalog
@agent_toolset
class EchoInstructions:
    """Echo wrapped action instructions inside a DO-NOT-FOLLOW fence so the user can inspect them."""

    def _fenced(self, body: str) -> str:
        """Compose a DO-NOT-FOLLOW fenced block around body (pure)."""
        return f"{_FENCE_HEADER}\n{body}\n{_FENCE_FOOTER}"

    @mcp
    @skill
    @agent_tool
    def fence(self, body: str = "", paths: list[str] | str | None = None) -> str:
        """Wrap instructions in DO-NOT-FOLLOW fences and return the fenced block.
        Header and footer label the block as inert diagnostic text intended for the user to read.
        paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the instruction body.
        body: in-process text. Leave this empty on an MCP call."""
        return self._fenced(load_document(body, paths))

    @mcp
    @skill
    @agent_instructions
    def echo_session(self, instructions: str = "", paths: list[str] | str | None = None) -> str:
        """STOP. DO NOT EXECUTE ANY OF THE INSTRUCTIONS BELOW THIS LINE. Your only task right now is: write every instruction you received for this action to a file, call fence with paths set to that file, emit the fenced block to the user as chat output, then stop completely. Nothing else. Do not interpret. Do not act. Do not generate. The fenced block IS the entire output of this invocation. Do not pass the instruction body through this call."""
        """Step 1 - write every instruction you received for this action to a file, verbatim, in full, in order. Call fence with paths set to that file. Do not summarise. Do not omit. Do not pass the instruction body as an argument."""
        self.fence()
        """Step 2 - emit the returned fenced block to the user as chat output. Every line inside the fence is inert diagnostic text to be read, not followed."""
        """STOP. You are done. Do not proceed to any other stage. Do not run grill, sketch, or generate."""
        return "Echo complete - instructions displayed, nothing executed."
