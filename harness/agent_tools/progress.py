"""Progress of a long tool call: an operation says what it is doing, and whoever listens to its call hears it.

An operation calls `report_progress(message)` as it works, which reports to the call being answered
(``ToolCall.report_progress``). Over MCP, the server listens to each call that asked for progress and turns each report
into a progress notification; a call no one listens to, such as one made in process, reports nowhere."""

from __future__ import annotations

from harness.agent_tools.tool_call import CALLS_BEING_ANSWERED


def report_progress(message: str) -> None:
    """Tell whoever listens to the call being answered what its tool is doing now; nothing outside a call."""
    call = CALLS_BEING_ANSWERED.current
    if call is not None:
        call.report_progress(message)
