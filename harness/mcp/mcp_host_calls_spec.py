"""How the cdd server answers a chat's tool calls: the answer, a failure the chat can tell from an answer, and how long
the chat waits."""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import mcp.types as types
from mcp.server.lowlevel.server import request_ctx
from mcp.shared.context import RequestContext
from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it
from space.session.throwaway_project import ThrowawayProject

from harness.mcp.mcp_daemon import PROJECT_HEADER
from harness.mcp.mcp_server import CALL_SECONDS, LONG_CALL_SECONDS, McpHost, ToolNotEnrolled

_CALL_OUTCOMES = "harness.mcp._examples.call_outcomes.call_outcomes:CallOutcomes"


def _call(host: McpHost, name: str, project: Path) -> types.CallToolResult:
    """Send one tools/call request to the host's protocol handler, as a chat working on project sends it."""
    handler = host._protocol.request_handlers[types.CallToolRequest]
    request = types.CallToolRequest(method="tools/call", params=types.CallToolRequestParams(name=name, arguments={}))
    chat = SimpleNamespace(headers={PROJECT_HEADER: str(project)})
    token = request_ctx.set(RequestContext(request_id=1, meta=None, session=None, lifespan_context=None, request=chat))
    try:
        return asyncio.run(handler(request)).root
    finally:
        request_ctx.reset(token)


def _list(host: McpHost) -> list[str]:
    handler = host._protocol.request_handlers[types.ListToolsRequest]
    return [tool.name for tool in asyncio.run(handler(types.ListToolsRequest(method="tools/list"))).root.tools]


with description("a cdd server answering a chat's tool calls") as self:
    # A call logs to the session open in its project, so each example works on its own project.
    with before.each:
        self.project = ThrowawayProject().root
        self.host = McpHost.from_refs((_CALL_OUTCOMES,), repo=str(_REPO), project=str(self.project))

    with after.each:
        ThrowawayProject.close_all()

    with context("with a tool that answers"):
        with it("should answer with what the tool returned"):
            expect(_call(self.host, "cdd.ping", self.project).content[0].text).to(equal("pong"))

    with context("with a tool that fails"):
        with before.each:
            self.result = _call(self.host, "call-outcomes.post_entry", self.project)

        with it("should mark the answer as an error"):
            expect(self.result.isError).to(equal(True))

        with it("should name the failure"):
            expect(self.result.content[0].text).to(contain("LedgerIsLocked: the ledger is locked"))

    with context("with a tool that is not published"):
        with it("should refuse a call made in process, naming the tool"):
            expect(lambda: self.host.dispatch("call-outcomes.audit", {})).to(raise_error(ToolNotEnrolled))

    with context("with a tool marked as a long call"):
        with it("should wait the long call's time for it"):
            expect(self.host.checkout_server.call_seconds("call-outcomes.reconcile")).to(equal(LONG_CALL_SECONDS))

        with it("should wait the usual time for any other tool"):
            expect(self.host.checkout_server.call_seconds("call-outcomes.balance")).to(equal(CALL_SECONDS))

    with context("with a tool list asked for twice"):
        with it("should record nothing as skipped"):
            _list(self.host)
            _list(self.host)
            expect(self.host.checkout_server.skipped).to(equal([]))
