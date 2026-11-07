"""The hooks that start the one cdd server: Cursor and VS Code connect to its URL and cannot start it themselves."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_toolset
from harness.hooks.hooks import hook
from harness.installation.destination import noCatalog
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_daemon import McpDaemon

if TYPE_CHECKING:
    from harness.hooks.hook_server import HookPayload

# The checkout this code runs from. The cdd server is installed into ``~/.cdd`` from it, whichever project's hook asks.
_CDD_CHECKOUT = Path(__file__).resolve().parents[2]


@noCatalog
@agent_toolset
class CddServerHooks:
    """Start the one cdd server when a chat starts and after every agent answer, so a chat in an IDE that cannot start
    it still finds it answering. Every install publishes these hooks beside the repository's own."""

    def __init__(self, home: CddHome | None = None) -> None:
        self.daemon = McpDaemon(home if home is not None else CddHome())
        self.checkout = _CDD_CHECKOUT

    @hook("sessionStart")
    def ensure_mcp_server_on_session_start(self, payload: HookPayload) -> str:
        """Start the cdd server when a chat starts."""
        return self.daemon.ensure_from(self.checkout)

    @hook("afterAgentResponse")
    def ensure_mcp_server_after_agent_response(self, payload: HookPayload) -> str:
        """Start the cdd server again after an agent answers, when it stopped during the answer."""
        return self.daemon.ensure_from(self.checkout)
