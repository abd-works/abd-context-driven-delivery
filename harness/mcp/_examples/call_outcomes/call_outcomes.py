"""A toolset whose calls end in each way a chat can meet: an answer, a failure, and a call that may take minutes."""
from __future__ import annotations

import time

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.tool_call import ToolCall
from harness.mcp.mcp_annotations import long_call, mcp


MONTH_END_SECONDS = 2


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
    def ledger_folder(self) -> str:
        """Answer the folder of the project the call works on, where the ledger is kept."""
        return str(ToolCall.answering().project)

    @mcp
    @agent_tool
    def clerk(self) -> str:
        """Answer the id of the chat the call came from, the clerk posting to the ledger."""
        return ToolCall.answering().chat_id

    @mcp
    @agent_tool
    def post_entry(self) -> str:
        """Fail, because the ledger is locked."""
        raise LedgerIsLocked("the ledger is locked for month end")

    @mcp
    @agent_tool
    def close_month(self) -> str:
        """Wait for month end, which takes longer than a diagnostics probe waits for any tool."""
        time.sleep(MONTH_END_SECONDS)
        return "closed"

    @mcp
    @long_call
    @agent_tool
    def reconcile(self) -> str:
        """Reconcile every account, which may take minutes."""
        return "reconciled"
