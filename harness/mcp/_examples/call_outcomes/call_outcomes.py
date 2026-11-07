"""A toolset whose calls end in each way a chat can meet: an answer, a failure, and a call that may take minutes."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import long_call, mcp


class LedgerIsLocked(Exception):
    """The ledger the spec's tool writes to is locked."""


@agent_toolset
class CallOutcomes:
    """Tools a host spec calls to see how the cdd server answers each outcome."""

    @mcp
    @agent_tool
    def balance(self) -> str:
        """Answer the ledger's balance."""
        return "42"

    @mcp
    @agent_tool
    def post_entry(self) -> str:
        """Fail, because the ledger is locked."""
        raise LedgerIsLocked("the ledger is locked for month end")

    @mcp
    @long_call
    @agent_tool
    def reconcile(self) -> str:
        """Reconcile every account, which may take minutes."""
        return "reconciled"
