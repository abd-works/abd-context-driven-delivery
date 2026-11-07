"""Infrastructure spec — the one cdd server, over HTTP, answering chats from many projects."""

import asyncio
import contextlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _path = str(_REPO_ROOT / _cat)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import anyio
import httpx
from expects import contain, equal, expect
from mamba import after, before, context, description, it
from mcp import McpError, types

from harness.mcp.spec_support import SpecServer

_LINGER_SECONDS = 1
_HOSTING_DEMO = "harness.mcp._examples.hosting_demo.hosting_demo:HostingDemo"
_ECHO = "tools.echo.echo:Echo"
_PARAMETER_TYPES = "harness.mcp._examples.parameter_types.parameter_types:ParameterTypes"
_RENDER = "cdd_guidance.actions.render.render:Render"
_SESSION = "space.session.sessions:Sessions"
_TOOLSETS = (_HOSTING_DEMO, _ECHO, _PARAMETER_TYPES, _RENDER, _SESSION)
_ECHO_ARGUMENTS = {
    "text": "parcel",
    "count": 2,
    "ratio": 1.5,
    "flag": True,
    "items": ["a", "b"],
    "fields": {"city": "depot"},
    "untyped_items": ["x"],
    "untyped_fields": {"k": "v"},
    "counted_items": [1, 2],
    "flagged_items": [True, False],
    "measured_items": [0.5],
    "nested_items": [["a"]],
    "record_items": [{"id": "1"}],
    "counted_fields": {"n": 3},
    "listed_fields": {"ns": [1, 2]},
}


def _text(result) -> str:
    return result.content[0].text


class ChatProbe:
    """What one chat does against the server, each in a project folder of its own so no call sees another's state."""

    def __init__(self, server: SpecServer) -> None:
        self.server = server

    def run(self, action, project: Path | None = None, seconds: float | None = None):
        folder = project or Path(tempfile.mkdtemp(prefix="cdd-chat-"))

        async def in_chat():
            async with self.server.chat(folder, seconds) as session:
                return await action(session)

        return asyncio.run(in_chat())

    async def increment_then_read_twice(self, session):
        await session.call_tool("hosting-demo.increment", arguments={"step": 4})
        first = await session.call_tool("hosting-demo.read_count", arguments={})
        await session.call_tool("hosting-demo.increment", arguments={"step": 1})
        second = await session.call_tool("hosting-demo.read_count", arguments={})
        return _text(first), _text(second)

    async def exercise(self, session):
        await session.call_tool("hosting-demo.plan_work", arguments={"concept": "widgets"})
        return _text(await session.call_tool("hosting-demo.read_count", arguments={}))

    async def cancel_running_call_then_ping(self, session):
        request_id = session._request_id

        async def lingering_call():
            with contextlib.suppress(McpError):
                await session.call_tool("hosting-demo.linger", arguments={"seconds": _LINGER_SECONDS})

        async with anyio.create_task_group() as group:
            group.start_soon(lingering_call)
            await anyio.sleep(_LINGER_SECONDS / 2)
            await session.send_notification(
                types.ClientNotification(
                    types.CancelledNotification(
                        params=types.CancelledNotificationParams(requestId=request_id, reason="spec")
                    )
                )
            )
        await anyio.sleep(_LINGER_SECONDS)
        return _text(await session.call_tool("cdd.ping", arguments={}))

    async def increment_restart_then_read(self, session):
        await session.call_tool("hosting-demo.increment", arguments={"step": 4})
        await session.call_tool("cdd.restart", arguments={})
        return _text(await session.call_tool("hosting-demo.read_count", arguments={}))

    async def restart_then_ping(self, session):
        await session.call_tool("cdd.restart", arguments={})
        return _text(await session.call_tool("cdd.ping", arguments={}))


class TwoWorktrees:
    """A repository with two worktrees, as two chats working on one project's branches see it."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-worktrees-")).resolve()
        self.main = self.root / "main"
        self.first = self.root / "first"
        self.second = self.root / "second"

    def create(self) -> None:
        self.main.mkdir()
        self._git(self.main, "init", "--quiet", "--initial-branch", "main")
        (self.main / "README.md").write_text("project\n", encoding="utf-8")
        self._git(self.main, "add", "README.md")
        self._git(self.main, "-c", "user.name=spec", "-c", "user.email=spec@example.com", "commit", "--quiet", "-m", "start")
        self._git(self.main, "worktree", "add", "--quiet", "-b", "first", str(self.first))
        self._git(self.main, "worktree", "add", "--quiet", "-b", "second", str(self.second))

    def remove(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def saved_session(self, worktree: Path) -> str:
        return json.loads((worktree / ".sessions" / "session.json").read_text(encoding="utf-8"))["session"]

    def _git(self, folder: Path, *arguments: str) -> None:
        subprocess.run(["git", *arguments], cwd=folder, check=True, capture_output=True)


with description("the cdd server") as self:
    with before.all:
        self.server = SpecServer(_TOOLSETS)
        self.started = self.server.start()
        self.chat = ChatProbe(self.server)

    with after.all:
        self.server.stop()

    with context("that a chat has connected"):
        with it("should expose the built-in health-check tool"):
            tools = self.chat.run(lambda session: session.list_tools())
            expect([tool.name for tool in tools.tools]).to(contain("cdd.ping"))

        with it("should expose the built-in restart tool"):
            tools = self.chat.run(lambda session: session.list_tools())
            expect([tool.name for tool in tools.tools]).to(contain("cdd.restart"))

        with it("should answer cdd.ping with pong"):
            result = self.chat.run(lambda session: session.call_tool("cdd.ping", arguments={}))
            expect(_text(result)).to(equal("pong"))

        with it("should answer the Cursor underscore alias cdd_ping with pong"):
            result = self.chat.run(lambda session: session.call_tool("cdd_ping", arguments={}))
            expect(_text(result)).to(equal("pong"))

        with it("should list HostingDemo @agent_tool operations"):
            names = [tool.name for tool in self.chat.run(lambda session: session.list_tools()).tools]
            expect(names).to(contain("hosting-demo.increment"))
            expect(names).to(contain("hosting-demo.read_count"))

        with it("should list no prompts when every enrolled operation is a tool"):
            prompts = self.chat.run(lambda session: session.list_prompts())
            expect([prompt.name for prompt in prompts.prompts]).to(equal([]))

        with it("should retain toolset state across calls on one project"):
            first, second = self.chat.run(self.chat.increment_then_read_twice)
            expect(first).to(equal("4"))
            expect(second).to(equal("5"))

        with context("with a HostingDemo operation that calls another @agent_tool"):
            with it("should run orchestration through tools/call"):
                result = self.chat.run(
                    lambda session: session.call_tool("hosting-demo.plan_work", arguments={"concept": "widgets"})
                )
                payload = json.loads(_text(result))
                expect(payload["concept"]).to(equal("widgets"))
                expect(payload["count"]).to(equal(2))

            with it("should advance toolset state from orchestrated @agent_tool calls"):
                expect(self.chat.run(self.chat.exercise)).to(equal("2"))

        with context("that has had a running tool call cancelled by the client"):
            with it("should keep answering later calls"):
                expect(self.chat.run(self.chat.cancel_running_call_then_ping)).to(equal("pong"))

        with context("that has invoked a real @agent_tool through the MCP wire"):
            with it("should return what the tool returned"):
                result = self.chat.run(
                    lambda session: session.call_tool("echo.fence", arguments={"body": "hello mcp"})
                )
                expect("hello mcp" in _text(result)).to(equal(True))

        with context("with the ParameterTypes toolset"):
            with it("should advertise a list parameter as a JSON Schema array"):
                tools = self.chat.run(lambda session: session.list_tools())
                echo = next(tool for tool in tools.tools if tool.name == "parameter-types.echo")
                expect(echo.inputSchema["properties"]["items"]["type"]).to(equal("array"))

            with it("should advertise a dict parameter as a JSON Schema object"):
                tools = self.chat.run(lambda session: session.list_tools())
                echo = next(tool for tool in tools.tools if tool.name == "parameter-types.echo")
                expect(echo.inputSchema["properties"]["fields"]["type"]).to(equal("object"))

            with it("should advertise a boolean parameter as JSON Schema boolean"):
                tools = self.chat.run(lambda session: session.list_tools())
                echo = next(tool for tool in tools.tools if tool.name == "parameter-types.echo")
                expect(echo.inputSchema["properties"]["flag"]["type"]).to(equal("boolean"))

            with it("should return every argument type unchanged"):
                result = self.chat.run(
                    lambda session: session.call_tool("parameter-types.echo", arguments=_ECHO_ARGUMENTS)
                )
                echoed = json.loads(_text(result))
                expect({key: echoed[key] for key in ("items", "flag", "fields", "count", "ratio", "nested_items")}).to(
                    equal({key: _ECHO_ARGUMENTS[key] for key in ("items", "flag", "fields", "count", "ratio", "nested_items")})
                )

            with it("should invoke a Sequence parameter with a JSON array"):
                result = self.chat.run(
                    lambda session: session.call_tool("parameter-types.echo_sequence", arguments={"value": ["stop", "drop"]})
                )
                expect(json.loads(_text(result))).to(equal(["stop", "drop"]))

            with it("should invoke a Mapping parameter with a JSON object"):
                result = self.chat.run(
                    lambda session: session.call_tool("parameter-types.echo_mapping", arguments={"value": {"n": 3}})
                )
                expect(json.loads(_text(result))).to(equal({"n": 3}))

        with context("that renders from a file path"):
            with it("should return the render within 10 seconds"):
                folder = Path(tempfile.mkdtemp(prefix="mcp-render-path-"))
                sketch = folder / "cart-sketch.md"
                sketch.write_text("Cart\n  owner\n", encoding="utf-8")
                arguments = {"guidance": ["clean-engineering-model"], "format": "python", "source": "sketch", "paths": [str(sketch)]}
                result = self.chat.run(lambda session: session.call_tool("render.render", arguments=arguments), folder, 10)
                expect(_text(result)).to(contain("Cart"))

    with context("that two chats in different worktrees have connected"):
        with before.each:
            self.worktrees = TwoWorktrees()
            self.worktrees.create()
            self.chat.run(lambda session: session.call_tool("sessions.switch", arguments={"name": "alpha"}), self.worktrees.first)
            self.chat.run(lambda session: session.call_tool("sessions.switch", arguments={"name": "beta"}), self.worktrees.second)

        with after.each:
            self.worktrees.remove()

        with it("should answer both chats from the one server process"):
            projects = self.server.daemon.ping["projects"]
            expect(self.server.daemon.ping["pid"]).to(equal(self.started["pid"]))
            expect(projects).to(contain(str(self.worktrees.first), str(self.worktrees.second)))

        with it("should save each chat's session in its own worktree"):
            saved = (self.worktrees.saved_session(self.worktrees.first), self.worktrees.saved_session(self.worktrees.second))
            expect(saved).to(equal(("alpha", "beta")))

        with it("should give each chat its own worktree's session"):
            def current(worktree: Path) -> str:
                result = self.chat.run(lambda session: session.call_tool("sessions.current", arguments={}), worktree)
                return json.loads(_text(result))["name"]

            expect((current(self.worktrees.first), current(self.worktrees.second))).to(equal(("alpha", "beta")))

        with it("should keep one worktree's toolset state out of the other"):
            self.chat.run(lambda session: session.call_tool("hosting-demo.increment", arguments={"step": 7}), self.worktrees.first)
            second = self.chat.run(lambda session: session.call_tool("hosting-demo.read_count", arguments={}), self.worktrees.second)
            expect(_text(second)).to(equal("0"))

    # Claude Code runs a chat's header helper again only when the server answers 401, so a chat that connected while
    # the helper could not run gets its project named on the next try instead of failing every call.
    with context("that a chat names no project"):
        with before.each:
            self.answer = httpx.post(self.server.url, json={"jsonrpc": "2.0", "id": 1, "method": "ping"}, headers={"Accept": "application/json, text/event-stream"})

        with it("should refuse the connection as unauthorized"):
            expect(self.answer.status_code).to(equal(401))

        with it("should say which header is missing"):
            expect(self.answer.text).to(contain("X-CDD-Project"))

    with context("that has been restarted"):
        with it("should start its toolsets again on the code as it is now"):
            expect(self.chat.run(self.chat.increment_restart_then_read)).to(equal("0"))

        with it("should keep answering on the same connection"):
            expect(self.chat.run(self.chat.restart_then_ping)).to(equal("pong"))

        with it("should still be the same process"):
            self.chat.run(self.chat.restart_then_ping)
            expect(self.server.daemon.ping["pid"]).to(equal(self.started["pid"]))


with description("the cdd connect script") as self:
    with before.each:
        self.server = SpecServer((_HOSTING_DEMO,))
        self.server.install()
        self.project = Path(tempfile.mkdtemp(prefix="cdd-connect-")).resolve()

    with after.each:
        self.server.stop()
        shutil.rmtree(self.project, ignore_errors=True)

    with context("that an IDE runs in a chat's folder while no server answers"):
        with before.each:
            done = subprocess.run(
                [sys.executable, str(self.server.home.connect_script)],
                cwd=self.project,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.headers = json.loads(done.stdout)

        with it("should start the server"):
            expect(self.server.daemon.is_running).to(equal(True))

        with it("should name the chat's folder as the project"):
            expect(self.headers).to(equal({"X-CDD-Project": str(self.project)}))
