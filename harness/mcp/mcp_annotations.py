"""The annotations an author types to publish an operation through the cdd server: ``@mcp`` and ``@long_call``.

They live apart from the server, which loads the MCP SDK, so a toolset that only annotates its operations loads none of
it."""
from __future__ import annotations

from harness.agent_tools.agent_tools import InstallDestination
from harness.annotations.annotation import Annotation, Destination


class Mcp(Destination):
    flag = "_mcp"
    channel = InstallDestination.MCP


mcp = Mcp


class LongCall(Annotation):
    """Annotate an MCP operation whose call may take minutes, such as one that walks the repository, waits on git over the
    network, or probes every other tool. The cdd server waits ``LONG_CALL_SECONDS`` for its answer, not
    ``CALL_SECONDS``, before telling the chat it is still running."""

    flag = "_long_call"


long_call = LongCall
