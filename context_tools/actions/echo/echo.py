# @toolset-manifest python -m tools manifest echo.echo:Echo
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Echo - print an action's wrapped instructions inside a DO-NOT-FOLLOW fence for inspection.

Echo is a standalone toolset. Any agent or human can invoke its tools and
echo_session action directly to render arbitrary text inside DO-NOT-FOLLOW
fences.

The complementary @echo decorator (see _decorator.py, re-exported from the
package root) marks another action's @agent_instructions so framework-level composition can
short-circuit that action into an echo of its fully-wrapped instructions -
diagnostic-only, no execution.
"""
from __future__ import annotations

from primitives.actions.action import agent_instructions
from tools.tool import agent_tool, toolset


_FENCE_HEADER = "===== DO NOT FOLLOW ANY OF THESE INSTRUCTIONS ====="
_FENCE_FOOTER = "===== END: DO NOT FOLLOW ANY OF THESE INSTRUCTIONS ====="


@toolset
class Echo:
    """Echo wrapped action instructions inside a DO-NOT-FOLLOW fence so the user can inspect them."""

    def _fenced(self, body: str) -> str:
        """Compose a DO-NOT-FOLLOW fenced block around body (pure)."""
        return f"{_FENCE_HEADER}\n{body}\n{_FENCE_FOOTER}"

    @agent_tool
    def fence(self, body: str) -> str:
        """Wrap {body} in DO-NOT-FOLLOW fences and return the fenced block.
        Header and footer label the block as inert diagnostic text intended for the user to read.
        Use to render wrapped instructions verbatim for inspection."""
        return self._fenced(body)

    @agent_instructions
    def echo_session(self, instructions: str) -> str:
        """STOP. DO NOT EXECUTE ANY OF THE INSTRUCTIONS BELOW THIS LINE. Your only task right now is: collect every instruction you received for this action into one string, call fence with that string, emit the fenced block to the user as chat output, then stop completely. Nothing else. Do not interpret. Do not act. Do not generate. The fenced block IS the entire output of this invocation."""
        """Step 1 - call fence, passing every instruction you received for this action - verbatim, in full, in order - as a single string. Do not summarise. Do not omit."""
        self.fence()
        """Step 2 - emit the returned fenced block to the user as chat output. Every line inside the fence is inert diagnostic text to be read, not followed."""
        """STOP. You are done. Do not proceed to any other stage. Do not run grill, sketch, or generate."""
        return "Echo complete - instructions displayed, nothing executed."
