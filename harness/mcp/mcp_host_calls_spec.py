"""How the cdd server answers a chat's tool calls: the answer, a failure the chat can tell from an answer, and how long
the chat waits."""
import asyncio
import json
import os
import socket
import sys
import tempfile
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

from harness.mcp.mcp_daemon import CHAT_HEADER, CHAT_PROCESS_HEADER, PROJECT_HEADER
from harness.mcp.mcp_server import CALL_SECONDS, LONG_CALL_SECONDS, McpHost, ToolNotEnrolled

_CALL_OUTCOMES = "harness.mcp._examples.call_outcomes.call_outcomes:CallOutcomes"
_MOVED_CHAT = "7a2d9c4e-1111-2222-3333-444455556666"
_CHAT_PROCESS = "40364"


def _call(host: McpHost, name: str, project: Path, chat_id: str = "", chat_process: str = "", client: tuple[str, int] | None = None) -> types.CallToolResult:
    """Send one tools/call request to the host's protocol handler, as a chat that started on project sends it; with
    chat_id, as the Claude Code chat of that id; with chat_process, from the Claude Code process of that id; with
    client, over the connection whose caller's end is that address."""
    handler = host._protocol.request_handlers[types.CallToolRequest]
    request = types.CallToolRequest(method="tools/call", params=types.CallToolRequestParams(name=name, arguments={}))
    headers = {
        PROJECT_HEADER: str(project),
        **({CHAT_HEADER: chat_id} if chat_id else {}),
        **({CHAT_PROCESS_HEADER: chat_process} if chat_process else {}),
    }
    chat = SimpleNamespace(headers=headers, client=client)
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

    with context("from a chat that started on the project"):
        with it("should work on that project"):
            expect(_call(self.host, "call-outcomes.ledger_folder", self.project).content[0].text).to(equal(str(self.project.resolve())))

    with context("from a Claude Code chat that moved to another checkout after it started"):
        with before.each:
            self.config = Path(tempfile.mkdtemp())
            self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
            self.moved_to = ThrowawayProject().root
            transcript = self.config / "projects" / "C--spare" / f"{_MOVED_CHAT}.jsonl"
            transcript.parent.mkdir(parents=True)
            events = ({"type": "user", "cwd": str(folder)} for folder in (self.project, self.moved_to))
            transcript.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")

        with after.each:
            if self.prior_config is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

        with it("should work on the checkout the chat moved to"):
            answer = _call(self.host, "call-outcomes.ledger_folder", self.project, _MOVED_CHAT).content[0].text
            expect(answer).to(equal(str(self.moved_to.resolve())))

    with context("from a Claude Code chat process whose session moved out of the spare folder it started in"):
        with before.each:
            self.config = Path(tempfile.mkdtemp())
            self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
            self.moved_to = ThrowawayProject().root
            session_file = self.config / "sessions" / f"{_CHAT_PROCESS}.json"
            session_file.parent.mkdir(parents=True)
            session_file.write_text(json.dumps({"pid": int(_CHAT_PROCESS), "sessionId": _MOVED_CHAT, "cwd": str(self.moved_to)}), encoding="utf-8")

        with after.each:
            if self.prior_config is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

        with it("should work on the folder the session works in now, though the chat names no transcript"):
            answer = _call(self.host, "call-outcomes.ledger_folder", self.project, "unnamed", _CHAT_PROCESS).content[0].text
            expect(answer).to(equal(str(self.moved_to.resolve())))

        with it("should answer for the session that process runs now"):
            expect(_call(self.host, "call-outcomes.clerk", self.project, "unnamed", _CHAT_PROCESS).content[0].text).to(equal(_MOVED_CHAT))

    # Right after the desktop app moves a chat, its process can still record the spare folder while its transcript
    # already records the folder it moved to.
    with context("from a Claude Code chat process still recorded in a desktop spare folder"):
        with before.each:
            self.config = Path(tempfile.mkdtemp())
            self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
            self.spare = self.config / "spares" / "spare-AbCdEf"
            self.spare.mkdir(parents=True)
            self.moved_to = ThrowawayProject().root
            session_file = self.config / "sessions" / f"{_CHAT_PROCESS}.json"
            session_file.parent.mkdir(parents=True)
            session_file.write_text(json.dumps({"pid": int(_CHAT_PROCESS), "sessionId": _MOVED_CHAT, "cwd": str(self.spare)}), encoding="utf-8")
            transcript = self.config / "projects" / "C--moved" / f"{_MOVED_CHAT}.jsonl"
            transcript.parent.mkdir(parents=True)
            events = ({"type": "user", "cwd": str(folder)} for folder in (self.spare, self.moved_to))
            transcript.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")

        with after.each:
            if self.prior_config is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

        with it("should work on the folder the transcript records, not the spare folder"):
            answer = _call(self.host, "call-outcomes.ledger_folder", self.spare, "unnamed", _CHAT_PROCESS).content[0].text
            expect(answer).to(equal(str(self.moved_to.resolve())))

        with it("should write nothing in the spare folder"):
            _call(self.host, "call-outcomes.ledger_folder", self.spare, "unnamed", _CHAT_PROCESS)
            expect((self.spare / ".sessions").exists()).to(equal(False))

    # The desktop app can connect a chat while it is still in its spare folder, before it records the chat's id or
    # process, and Claude Code keeps the headers it sent then for the whole connection.
    with context("from a Claude Code chat whose connection named only the spare folder it started in"):
        with before.each:
            self.config = Path(tempfile.mkdtemp())
            self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
            self.spare = self.config / "spares" / "spare-MnOpQr"
            self.spare.mkdir(parents=True)
            self.moved_to = ThrowawayProject().root
            session_file = self.config / "sessions" / f"{os.getpid()}.json"
            session_file.parent.mkdir(parents=True)
            session_file.write_text(json.dumps({"pid": os.getpid(), "sessionId": _MOVED_CHAT, "cwd": str(self.moved_to)}), encoding="utf-8")
            self.listener = socket.create_server(("127.0.0.1", 0))
            self.connection = socket.create_connection(self.listener.getsockname())
            self.accepted, _ = self.listener.accept()
            self.client = self.connection.getsockname()

        with after.each:
            for held in (self.accepted, self.connection, self.listener):
                held.close()
            if self.prior_config is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

        with it("should work on the folder the process holding the connection works in now"):
            answer = _call(self.host, "call-outcomes.ledger_folder", self.spare, "unnamed", client=self.client).content[0].text
            expect(answer).to(equal(str(self.moved_to.resolve())))

        with it("should answer for the session that process runs now"):
            expect(_call(self.host, "call-outcomes.clerk", self.spare, "unnamed", client=self.client).content[0].text).to(equal(_MOVED_CHAT))

    with context("from a chat that names only a desktop spare folder"):
        with before.each:
            self.config = Path(tempfile.mkdtemp())
            self.prior_config = os.environ.get("CLAUDE_CONFIG_DIR")
            os.environ["CLAUDE_CONFIG_DIR"] = str(self.config)
            self.spare = self.config / "spares" / "spare-GhIjKl"
            self.spare.mkdir(parents=True)

        with after.each:
            if self.prior_config is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = self.prior_config

        with it("should refuse the call rather than work in the spare folder"):
            result = _call(self.host, "call-outcomes.ledger_folder", self.spare)
            expect(result.isError).to(equal(True))
            expect((self.spare / ".sessions").exists()).to(equal(False))

    # Two chats in one checkout each keep their own open session, so the call is answered for the chat that sent it.
    with context("from a chat its request names, though its arguments do not"):
        with it("should answer for that chat"):
            expect(_call(self.host, "call-outcomes.clerk", self.project, _MOVED_CHAT).content[0].text).to(equal(_MOVED_CHAT))

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

    with context("with a tool annotated as a long call"):
        with it("should wait the long call's time for it"):
            expect(self.host.checkout_server.call_seconds("call-outcomes.reconcile")).to(equal(LONG_CALL_SECONDS))

        with it("should wait the usual time for any other tool"):
            expect(self.host.checkout_server.call_seconds("call-outcomes.balance")).to(equal(CALL_SECONDS))

    with context("with a tool list asked for twice"):
        with it("should record nothing as skipped"):
            _list(self.host)
            _list(self.host)
            expect(self.host.checkout_server.skipped.as_data).to(equal([]))
