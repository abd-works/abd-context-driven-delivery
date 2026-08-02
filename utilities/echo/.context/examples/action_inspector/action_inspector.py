"""ActionInspector - wrap action instructions in a DO-NOT-FOLLOW fence for inspection."""
from __future__ import annotations

from utilities.echo.echo import Echoer


class ActionInspector:
    """Render action instructions inside a DO-NOT-FOLLOW fence so they can be read safely."""

    def inspect(self, instructions: str) -> str:
        """Wrap instructions in DO-NOT-FOLLOW fences and return the fenced block.

        Passes instructions verbatim to Echoer.fence, which surrounds them with
        a header and footer line that marks the block as inert diagnostic text.
        The returned string is safe to emit to the user for inspection without
        any risk of the agent acting on the instructions.
        """
        echoer = Echoer()
        return echoer.fence(instructions)
