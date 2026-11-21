"""One request a chat sent the cdd server: the project a tool it calls works on, read from the request's headers. No
Claude Code process is named and no connection is held, so the project comes from the headers alone."""
import tempfile
from pathlib import Path

from expects import be_none, equal, expect, raise_error
from mamba import before, context, description, it

from harness.mcp.mcp_address import PROJECT_HEADER
from harness.mcp.mcp_server import BUILTIN_PING_TOOL, ChatRequest, ProjectIsClaudeSettings, ProjectNotNamed

_SETTINGS = Path(tempfile.gettempdir()) / "claude-settings"


with description("a chat's request to the cdd server") as self:
    with context("that names its project"):
        with before.each:
            self.project = Path(tempfile.mkdtemp(prefix="chat-request-"))
            self.request = ChatRequest({PROJECT_HEADER: str(self.project)}, None, _SETTINGS)

        with it("should work on that project"):
            expect(self.request.project_for("session.show")).to(equal(self.project))

        with it("should come from no chat it can name"):
            expect(self.request.chat).to(be_none)

    with context("that names no project"):
        with before.each:
            self.request = ChatRequest({}, None, _SETTINGS)

        with it("should refuse a tool that needs one, naming the tool"):
            expect(lambda: self.request.project_for("session.show")).to(raise_error(ProjectNotNamed))

        with it("should let the ping through"):
            expect(self.request.project_for(BUILTIN_PING_TOOL)).to(be_none)

    with context("that names Claude Code's own settings folder as its project"):
        with it("should refuse it"):
            request = ChatRequest({PROJECT_HEADER: str(_SETTINGS)}, None, _SETTINGS.resolve())
            expect(lambda: request.project_for("session.show")).to(raise_error(ProjectIsClaudeSettings))
