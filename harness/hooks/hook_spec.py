"""BDD specs for installer @Hook dispatch."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools",):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("hooks", None)

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it
from harness.agent_tools import agent_toolset

from harness.agent_tools.agent_tools import agent_tool
from harness.hooks.hook_server import CursorEvent, HandlerCatalog, HookPayload, HookServer
from harness.hooks.hooks import Hook, Hooks
from installation.installer import Installer


def _dispatch(payload: dict, toolsets: list | None = None) -> dict:
    catalog = HandlerCatalog(toolsets or [], _REPO_ROOT)
    return HookServer(_REPO_ROOT, catalog).dispatch(HookPayload(payload)).as_dict()


def _dispatch_work_session_inject(tmp: tempfile.TemporaryDirectory):
    root = Path(tmp.name)
    session = root / ".sessions" / "work-session"
    session.mkdir(parents=True)
    (root / ".sessions" / "_active").write_text("work-session", encoding="utf-8")
    (session / "work-guidelines.md").write_text(
        "#### Rules\n\n"
        "- `put-logic-on-the-owning-resource` - session body of put-logic\n"
        "  star: 2\n"
        "  last-fail: 1\n"
        "  mistake: parked the check on the client\n"
        "  correction: call validate on the transaction\n",
        encoding="utf-8",
    )

    @agent_toolset
    class _PracticeInject:
        @Hook("postToolUse")
        def on_inject(self, payload: dict) -> dict:
            return {
                "additional_context": (
                    "- `put-logic-on-the-owning-resource` - practice body of put-logic\n"
                    "- `hide-inner-details` - Expose behavior through named operations."
                )
            }

    server = HookServer(root, HandlerCatalog([_PracticeInject], root))
    result = server.dispatch(
        HookPayload({"hook_event_name": "postToolUse", "tool_name": "Write"})
    )
    server._publish_context(result)
    server._write_last_chat_injected(result)
    return root, result


@Hooks(disabled=True)
@agent_toolset
class _DisabledFixture:
    calls: list[str] = []

    @Hook("afterAgentResponse")
    def on_after(self, payload: dict) -> dict:
        type(self).calls.append("after")
        return {"agent_message": "ran"}


@agent_toolset
class _DispatchFixture:
    calls: list[str] = []

    @Hook("afterAgentResponse")
    def on_after(self, payload: dict) -> dict:
        type(self).calls.append("after")
        return {"agent_message": "ran"}


@agent_toolset
class _StopFixture:
    calls: list[str] = []

    @Hook("stop")
    def on_stop(self, payload: dict) -> dict:
        type(self).calls.append("stop")
        return {"followup_message": "/turn"}


@agent_toolset
class _HookToolset:
    @Hook("stop")
    def on_stop(self, payload: dict) -> dict:
        return {}


@agent_toolset
class _ToolOnlyToolset:
    @agent_tool
    def ping(self) -> str:
        return "ok"


with description("a handler catalog"):

    with context("built from agent toolsets"):

        with it("should take hook operations from toolset tools"):
            catalog = HandlerCatalog([_HookToolset(), _ToolOnlyToolset()])
            handlers = catalog.for_event(CursorEvent("stop"))
            expect([handler.owner for handler in handlers]).to(equal([_HookToolset]))
            expect([handler.operation for handler in handlers]).to(equal(["on_stop"]))


with description("hook dispatch"):

    with context("that receives an afterAgentResponse payload"):

        with it("should skip handlers when the toolset is annotated hooks disabled"):
            _DisabledFixture.calls = []
            out = _dispatch(
                {"hook_event_name": "afterAgentResponse"},
                toolsets=[_DisabledFixture],
            )
            expect(out).to(equal({"permission": "allow"}))
            expect(_DisabledFixture.calls).to(equal([]))

        with it("should invoke handlers when the toolset is not disabled"):
            _DispatchFixture.calls = []
            out = _dispatch(
                {"hook_event_name": "afterAgentResponse"},
                toolsets=[_DispatchFixture],
            )
            expect(out["permission"]).to(equal("allow"))
            expect(out["agent_message"]).to(equal("ran"))
            expect(_DispatchFixture.calls).to(equal(["after"]))

    with context("that receives a stop payload"):

        with it("should pass through followup_message from enabled handlers"):
            _StopFixture.calls = []
            out = _dispatch({"hook_event_name": "stop"}, toolsets=[_StopFixture])
            expect(out).to(equal({"permission": "allow", "followup_message": "/turn"}))
            expect(_StopFixture.calls).to(equal(["stop"]))

        with it("should keep user_message separate from agent_message"):
            @agent_toolset
            class _MessageFixture:
                @Hook("beforeSubmitPrompt")
                def on_before(self, payload: dict) -> dict:
                    return {
                        "user_message": "for user",
                        "agent_message": "for agent",
                    }

            out = _dispatch(
                {"hook_event_name": "beforeSubmitPrompt"},
                toolsets=[_MessageFixture],
            )
            expect(out["user_message"]).to(equal("for user"))
            expect(out["agent_message"]).to(equal("for agent"))

        with it("should keep additional_context from every handler"):
            @agent_toolset
            class _FirstRules:
                @Hook("preToolUse")
                def on_first(self, payload: dict) -> dict:
                    return {"additional_context": "clean engineering code rules"}

            @agent_toolset
            class _SecondRules:
                @Hook("preToolUse")
                def on_second(self, payload: dict) -> dict:
                    return {"additional_context": "ddd tactics rules"}

            out = _dispatch(
                {"hook_event_name": "preToolUse", "tool_name": "Write"},
                toolsets=[_FirstRules, _SecondRules],
            )
            expect(out.get("additional_context") or "").to(
                contain("clean engineering code rules")
            )
            expect(out.get("additional_context") or "").to(contain("ddd tactics rules"))

        with it("should keep a repeated additional_context body once"):
            @agent_toolset
            class _Once:
                @Hook("postToolUse")
                def on_first(self, payload: dict) -> dict:
                    return {"additional_context": "keep-operations-small-focused"}

            @agent_toolset
            class _Again:
                @Hook("postToolUse")
                def on_second(self, payload: dict) -> dict:
                    return {"additional_context": "keep-operations-small-focused"}

            out = _dispatch(
                {"hook_event_name": "postToolUse", "tool_name": "Write"},
                toolsets=[_Once, _Again],
            )
            text = out.get("additional_context") or ""
            expect(text.count("keep-operations-small-focused")).to(equal(1))

        with it("should overwrite an injected rule of the same name from the work session"):
            tmp = tempfile.TemporaryDirectory()
            try:
                root, result = _dispatch_work_session_inject(tmp)
                text = result.additional_context or ""
                expect(text).to(contain("session body of put-logic"))
                expect(text).to(contain("parked the check on the client"))
                expect(text).not_to(contain("practice body of put-logic"))
                expect(text).to(contain("hide-inner-details"))
                expect(
                    text.find("session body of put-logic")
                    < text.find("hide-inner-details")
                ).to(equal(True))
            finally:
                tmp.cleanup()

        with it("should write last-chat-injected-rules after sending additional context"):
            tmp = tempfile.TemporaryDirectory()
            try:
                root, result = _dispatch_work_session_inject(tmp)
                dumped = (
                    root
                    / ".sessions"
                    / "work-session"
                    / "last-chat-injected-rules.md"
                ).read_text(encoding="utf-8")
                expect(dumped.strip()).to(equal((result.additional_context or "").strip()))
            finally:
                tmp.cleanup()

    with context("that invokes a handler whose tool has a docstring"):

        with it("should put that description on the hook event as agent_message"):
            @agent_toolset
            class _DescribedFixture:
                @Hook("preToolUse")
                def on_pre_tool(self, payload: dict) -> dict:
                    """Honor the hook operation description."""
                    return {"permission": "allow"}

            out = _dispatch({"hook_event_name": "preToolUse"}, toolsets=[_DescribedFixture])
            expect(out["agent_message"]).to(equal("Honor the hook operation description."))
            expect(out["permission"]).to(equal("allow"))

    with context("that parses stdin payloads"):

        with it("should strip a UTF-8 BOM"):
            raw = b'\xef\xbb\xbf{"hook_event_name":"stop"}'
            expect(HookPayload.from_stdin(raw).as_dict()).to(
                equal({"hook_event_name": "stop"})
            )


with description("session hook logs"):

    with context("when no work session is active"):

        with it("should create default session logs under .sessions/default/logs"):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                from harness.hooks.session_logs import SessionLogs

                logs = SessionLogs(root)
                folder = logs.ensure_default_session()
                expect(folder.is_dir()).to(be_true)
                log = logs.session_log_path("prompt-log.txt")
                expect(log.parent.as_posix()).to(
                    equal((root / ".sessions/default/logs").as_posix())
                )
                log.write_text("probe\n", encoding="utf-8")
                expect(log.is_file()).to(be_true)
                expect((folder / "session.md").is_file()).to(be_true)


with description("a hook server") as self:
    with context("that has stood up without a handlers file"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.server = HookServer.from_handlers(
                Path(self._tmp) / "missing.json", repo=self._tmp
            )

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should answer ping with pong"):
            expect(self.server.diagnose()["ping"]).to(equal("pong"))

    with context("that has stood up from written hook handlers"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            dest = Path(self._tmp) / "hook-handlers.json"
            dest.write_text(
                json.dumps(
                    {
                        "handlers": [
                            {
                                "event": "stop",
                                "operation": "auto_turn",
                                "ref": "harness.guidance.fixtures.agentic_ops.hook_ops:SampleHookOps",
                            }
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            self.server = HookServer.from_handlers(dest, repo=self._tmp)

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should list the installed hook event"):
            expect(self.server.diagnose()["events"]).to(contain("stop"))

    with context("that has stood up from handlers listing a toolset that cannot be loaded"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            dest = Path(self._tmp) / "hook-handlers.json"
            dest.write_text(
                json.dumps(
                    {
                        "handlers": [
                            {"event": "stop", "operation": "missing", "ref": "missing.module:Nope"},
                            {
                                "event": "stop",
                                "operation": "auto_turn",
                                "ref": "harness.guidance.fixtures.agentic_ops.hook_ops:SampleHookOps",
                            },
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            self.server = HookServer.from_handlers(dest, repo=self._tmp)

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should still answer ping"):
            expect(self.server.diagnose()["ping"]).to(equal("pong"))

        with it("should still list the loadable hook event"):
            expect(self.server.diagnose()["events"]).to(contain("stop"))

        with it("should diagnose the skipped toolset as an exception"):
            expect(self.server.diagnose()["exceptions"][0]["tool"]).to(
                equal("missing.module:Nope")
            )

        with it("should keep a chat notice naming the skipped toolset"):
            expect(self.server.diagnose()["notice"]).to(contain("missing.module:Nope"))

    with context("that dispatches to a handler that raises"):
        with before.each:
            @agent_toolset
            class _RaisingFixture:
                @Hook("stop")
                def on_stop(self, payload: dict) -> dict:
                    raise RuntimeError("handler misconfigured")

            self.server = HookServer(_REPO_ROOT, HandlerCatalog([_RaisingFixture], _REPO_ROOT))
            self.server.dispatch(HookPayload({"hook_event_name": "stop"}))

        with it("should still allow the event"):
            expect(
                self.server.dispatch(HookPayload({"hook_event_name": "stop"})).permission
            ).to(equal("allow"))

        with it("should diagnose the skipped handler as an exception"):
            expect(self.server.diagnose()["exceptions"][0]["tool"]).to(
                contain("on_stop")
            )


with description("the Cursor hook_server.py command"):

    with it("should dispatch sessionStart over stdin without an import error"):
        proc = subprocess.run(
            [
                sys.executable,
                "-u",
                str(_REPO_ROOT / "harness" / "hooks" / "hook_server.py"),
            ],
            input=b'{"hook_event_name":"sessionStart"}',
            cwd=str(_REPO_ROOT),
            capture_output=True,
            env={**os.environ, "PYTHONPATH": Installer(repo=_REPO_ROOT).pythonpath()},
        )
        expect(proc.returncode).to(equal(0))
        expect(json.loads(proc.stdout.decode("utf-8"))["permission"]).to(equal("allow"))
