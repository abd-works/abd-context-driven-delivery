"""Specs for the project a tool call works on, which follows the folder its chat works in now."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from harness.agent_tools.tool_call import ToolCall


with description("a tool call a chat sent"):
    with before.each:
        self.connected_from = Path(tempfile.mkdtemp(prefix="spare-"))
        self.worktree = Path(tempfile.mkdtemp(prefix="worktree-"))

    with context("that names the folder its chat works in now"):
        with before.each:
            self.call = ToolCall.sent({"chat_folder": str(self.worktree), "path": "cart.py"}, self.connected_from)

        with it("should work on the chat's folder, not the one it connected from"):
            expect(self.call.project).to(equal(self.worktree.resolve()))

        with it("should leave the tool only its own arguments"):
            expect(self.call.arguments).to(equal({"path": "cart.py"}))

    with context("that names no folder"):
        with it("should work on the project its header names"):
            expect(ToolCall.sent({"path": "cart.py"}, self.connected_from).project).to(equal(self.connected_from.resolve()))


with description("a tool call one lane's server hands the other's"):
    with before.each:
        from harness.agent_tools.chat_pointer import ChatPointer
        from harness.agent_tools.tool_call import ToolRequest

        self.project = Path(tempfile.mkdtemp(prefix="project-"))
        chat = ChatPointer("0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d")
        self.host = object()
        self.sent = ToolCall({"path": "cart.py"}, self.project, ToolRequest(chat, "graph.refresh")).as_sent()
        self.received = ToolCall.from_sent(self.sent, self.host)

    with it("should arrive naming the same tool"):
        expect(self.received.request.tool).to(equal("graph.refresh"))

    with it("should arrive with the same arguments, on the same project"):
        expect((self.received.arguments, self.received.project)).to(equal(({"path": "cart.py"}, self.project.resolve())))

    with it("should arrive from the same chat"):
        expect(self.received.chat_id).to(equal("0b1e2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"))

    with it("should be answered for that chat by the host that received it"):
        expect((self.received.request.mcp_host, self.received.request.answers_a_chat)).to(equal((self.host, True)))
