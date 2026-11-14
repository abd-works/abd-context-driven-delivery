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
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("hooks", None)

from expects import be, be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it
from harness.agent_tools import agent_toolset

from harness.agent_tools.agent_tools import agent_tool
from harness.hooks.hook_server import (
    HandlerCatalog,
    HookPayload,
    HookResult,
    HookServer,
)
from harness.hooks.hooks import Hook, Hooks, hook
from harness.installation.ide_layout import IdeLayout
from harness.installation.repository_toolsets import RepositoryToolsets
from space.session.sessions import Sessions
from space.work_state import WorkState
from cdd_guidance.actions.sketch.sketch import Sketch
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering


def _dispatch(payload: dict, toolsets: list | None = None) -> dict:
    catalog = HandlerCatalog(toolsets or [], _REPO_ROOT)
    return HookServer(_REPO_ROOT, catalog).dispatch(HookPayload(payload)).as_dict()


def _dispatch_work_session_inject(tmp: tempfile.TemporaryDirectory):
    """Run a postToolUse hook that injects rules while ``work-session`` is the active session."""
    root = Path(tmp.name)
    (root / ".sessions" / "work-session").mkdir(parents=True)
    WorkState(root).session = "work-session"

    @agent_toolset
    class _PracticeInject:
        @hook("postToolUse")
        def on_inject(self, payload: HookPayload) -> dict:
            return {
                "additional_context": (
                    "- `put-logic-on-the-owning-resource` - practice body of put-logic\n"
                    "- `hide-inner-details` - Expose behavior through named operations."
                )
            }

    server = HookServer(root, HandlerCatalog([_PracticeInject], root))
    result = server.handle_stdin(
        json.dumps({"hook_event_name": "postToolUse", "tool_name": "Write"}).encode()
    )
    return root, result


@Hooks(disabled=True)
@agent_toolset
class _DisabledFixture:
    calls: list[str] = []

    @hook("afterAgentResponse")
    def on_after(self, payload: HookPayload) -> dict:
        type(self).calls.append("after")
        return {"agent_message": "ran"}


@agent_toolset
class _DispatchFixture:
    calls: list[str] = []

    @hook("afterAgentResponse")
    def on_after(self, payload: HookPayload) -> dict:
        type(self).calls.append("after")
        return {"agent_message": "ran"}


@agent_toolset
class _StopFixture:
    calls: list[str] = []

    @hook("stop")
    def on_stop(self, payload: HookPayload) -> dict:
        type(self).calls.append("stop")
        return {"followup_message": "/turn"}


@agent_toolset
class _PatternInject:
    pattern = "lern_domain_driven"
    calls: list[str] = []

    @hook("postToolUse")
    def inject_rules(self, payload: HookPayload) -> dict:
        type(self).calls.append("lern")
        return {"additional_context": "lern rules"}


@agent_toolset
class _PayloadReader:
    seen: list[HookPayload] = []

    @hook("postToolUse")
    def on_used(self, payload: HookPayload) -> dict:
        type(self).seen.append(payload)
        return {}


@agent_toolset
class _CoreInject:
    calls: list[str] = []

    @hook("postToolUse")
    def inject_rules(self, payload: HookPayload) -> dict:
        type(self).calls.append("core")
        return {"additional_context": "core rules"}


def _guidelines_dispatch(root: Path, toolsets: list, guidelines: dict | None = None) -> dict:
    if guidelines is not None:
        from harness.installation.context_config import ContextConfig

        ContextConfig(root).update(guidelines=guidelines)
    server = HookServer(root, HandlerCatalog(toolsets, root))
    return server.dispatch(
        HookPayload(
            {
                "hook_event_name": "postToolUse",
                "tool_name": "Write",
                "workspace_roots": [str(root)],
                "tool_input": {"path": "src/customer/customer.ts"},
            }
        )
    ).as_dict()


@agent_toolset
class _HookToolset:
    @hook("stop")
    def on_stop(self, payload: HookPayload) -> dict:
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
            handlers = catalog.for_event("stop")
            expect([handler.label for handler in handlers]).to(equal(["_HookToolset.on_stop"]))

        with it("should hold the toolset's own agent tool for each hook operation"):
            toolset = _HookToolset()
            handler = HandlerCatalog([toolset]).for_event("stop")[0]
            expect(handler.tool.hook_event).to(equal("stop"))


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

    with context("that gates pattern hooks on config.json guidelines"):

        with it("should skip a pattern when the workspace leaves it disabled"):
            _PatternInject.calls = []
            with tempfile.TemporaryDirectory() as tmp:
                out = _guidelines_dispatch(
                    Path(tmp),
                    [_PatternInject],
                    {"lern_domain_driven": "disabled"},
                )
            expect(_PatternInject.calls).to(equal([]))
            expect(out).to(equal({"permission": "allow"}))

        with it("should skip a pattern when the workspace has no config.json"):
            _PatternInject.calls = []
            with tempfile.TemporaryDirectory() as tmp:
                out = _guidelines_dispatch(Path(tmp), [_PatternInject])
            expect(_PatternInject.calls).to(equal([]))
            expect(out).to(equal({"permission": "allow"}))

        with it("should run a pattern when the workspace enables it"):
            _PatternInject.calls = []
            with tempfile.TemporaryDirectory() as tmp:
                out = _guidelines_dispatch(
                    Path(tmp),
                    [_PatternInject],
                    {"lern-domain-driven": "enabled"},
                )
            expect(_PatternInject.calls).to(equal(["lern"]))
            expect(out["additional_context"]).to(equal("lern rules"))

        with it("should run a core practice when patterns are disabled"):
            _PatternInject.calls = []
            _CoreInject.calls = []
            with tempfile.TemporaryDirectory() as tmp:
                out = _guidelines_dispatch(
                    Path(tmp),
                    [_PatternInject, _CoreInject],
                    {"lern_domain_driven": "disabled"},
                )
            expect(_PatternInject.calls).to(equal([]))
            expect(_CoreInject.calls).to(equal(["core"]))
            expect(out["additional_context"]).to(equal("core rules"))

    with context("that receives a stop payload"):

        with it("should pass through followup_message from enabled handlers"):
            _StopFixture.calls = []
            out = _dispatch({"hook_event_name": "stop"}, toolsets=[_StopFixture])
            expect(out).to(equal({"permission": "allow", "followup_message": "/turn"}))
            expect(_StopFixture.calls).to(equal(["stop"]))

        with it("should give Cursor only followup_message for a stop reply"):
            delivered = HookResult.from_handler(
                {"followup_message": "These rules are injected in the chat."}
            )
            expect(delivered.as_dict()).to(
                equal({"followup_message": "These rules are injected in the chat."})
            )

        with it("should keep user_message separate from agent_message"):
            @agent_toolset
            class _MessageFixture:
                @hook("beforeSubmitPrompt")
                def on_before(self, payload: HookPayload) -> dict:
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
                @hook("preToolUse")
                def on_first(self, payload: HookPayload) -> dict:
                    return {"additional_context": "clean engineering code rules"}

            @agent_toolset
            class _SecondRules:
                @hook("preToolUse")
                def on_second(self, payload: HookPayload) -> dict:
                    return {"additional_context": "ddd tactics rules"}

            out = _dispatch(
                {"hook_event_name": "preToolUse", "tool_name": "Write"},
                toolsets=[_FirstRules, _SecondRules],
            )
            expect(out.get("additional_context") or "").to(
                contain("clean engineering code rules")
            )
            expect(out.get("additional_context") or "").to(contain("ddd tactics rules"))

        with it("should run inject_rules when a file edit arrives as afterFileEdit"):
            @agent_toolset
            class _FileEditRules:
                @hook("postToolUse")
                def inject_rules(self, payload: HookPayload) -> dict:
                    return {"additional_context": payload.get("file_path") or ""}

            out = _dispatch(
                {
                    "hook_event_name": "afterFileEdit",
                    "file_path": "sandbox/mm3e/no-yaml/story-map.md",
                },
                toolsets=[_FileEditRules],
            )
            expect(out.get("additional_context") or "").to(
                contain("sandbox/mm3e/no-yaml/story-map.md")
            )

        with it("should keep a repeated additional_context body once"):
            @agent_toolset
            class _Once:
                @hook("postToolUse")
                def on_first(self, payload: HookPayload) -> dict:
                    return {"additional_context": "keep-operations-small-focused"}

            @agent_toolset
            class _Again:
                @hook("postToolUse")
                def on_second(self, payload: HookPayload) -> dict:
                    return {"additional_context": "keep-operations-small-focused"}

            out = _dispatch(
                {"hook_event_name": "postToolUse", "tool_name": "Write"},
                toolsets=[_Once, _Again],
            )
            text = out.get("additional_context") or ""
            expect(text.count("keep-operations-small-focused")).to(equal(1))

        with it("should inject saved rules only into the chat that edited"):
            tmp = tempfile.TemporaryDirectory()
            try:
                root = Path(tmp.name)

                @agent_toolset
                class _ChatInject:
                    @hook("postToolUse")
                    def on_inject(self, payload: HookPayload) -> dict:
                        return {"additional_context": "stories scenario rules"}

                server = HookServer(root, HandlerCatalog([_ChatInject], root))
                server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "postToolUse",
                            "tool_name": "Write",
                            "conversation_id": "chat-a",
                            "tool_input": {"path": "story-map.md"},
                        }
                    ).encode()
                )
                shared = root / ".cursor" / "rules" / "practices" / "chat-inject.mdc"
                expect(shared.is_file()).to(equal(False))
                other = server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "beforeSubmitPrompt",
                            "conversation_id": "chat-b",
                        }
                    ).encode()
                )
                expect(other.additional_context or "").to(equal(""))
                same = server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "beforeSubmitPrompt",
                            "conversation_id": "chat-a",
                        }
                    ).encode()
                )
                expect(same.additional_context or "").to(contain("stories scenario rules"))
            finally:
                tmp.cleanup()

        with it("should not replay a read injection on the next prompt"):
            tmp = tempfile.TemporaryDirectory()
            try:
                root = Path(tmp.name)
                server = HookServer(root, HandlerCatalog([], root))
                saved = Sessions(root).current().chat_injections.path_for("chat-a")
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_text(
                    "Before you continue, echo the following message to the user:\n\nrules injected for clean-engineering-code\n",
                    encoding="utf-8",
                )
                replayed = server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "beforeSubmitPrompt",
                            "conversation_id": "chat-a",
                        }
                    ).encode()
                )
                expect(replayed.additional_context or "").to(equal(""))
            finally:
                tmp.cleanup()

        with it("should drop a saved edit-rules dump instead of replaying it"):
            tmp = tempfile.TemporaryDirectory()
            try:
                root = Path(tmp.name)
                server = HookServer(root, HandlerCatalog([], root))
                saved = Sessions(root).current().chat_injections.path_for("chat-a")
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_text(
                    "You just edited session.py. Check that edit against these rules and fix anything that does not follow them:\n"
                    "The following rules need to be followed while editing this document:\n"
                    "hide-inner-details\n",
                    encoding="utf-8",
                )
                replayed = server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "beforeSubmitPrompt",
                            "conversation_id": "chat-a",
                        }
                    ).encode()
                )
                expect(replayed.additional_context or "").to(equal(""))
                expect(saved.is_file()).to(equal(False))
            finally:
                tmp.cleanup()

        with it("should not submit the rules notice as the next user message"):
            tmp = tempfile.TemporaryDirectory()
            try:
                root = Path(tmp.name)

                @agent_toolset
                class _EditCheck:
                    @hook("postToolUse")
                    def inject_rules(self, payload: HookPayload) -> dict:
                        path = (payload.get("tool_input") or {}).get("path") or ""
                        if path.endswith("story-map.md"):
                            return {
                                "additional_context": (
                                    "These rules are injected in the chat.\n"
                                    "The user sees the chat line. Do not paste the rule text into the chat.\n"
                                    "--- chat ---\n"
                                    "rules injected for stories-story-map\n"
                                    "--- end chat ---\n"
                                    "verb-noun-format"
                                )
                            }
                        return {"additional_context": "later read rules"}

                server = HookServer(root, HandlerCatalog([_EditCheck], root))
                server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "afterFileEdit",
                            "conversation_id": "chat-a",
                            "file_path": "story-map.md",
                            "tool_input": {"path": "story-map.md"},
                        }
                    ).encode()
                )
                stopped = server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "stop",
                            "conversation_id": "chat-a",
                        }
                    ).encode()
                )
                expect(stopped.followup_message).to(equal(None))
                replayed = server.handle_stdin(
                    json.dumps(
                        {
                            "hook_event_name": "beforeSubmitPrompt",
                            "conversation_id": "chat-a",
                        }
                    ).encode()
                )
                text = replayed.additional_context or ""
                expect(text).to(equal("verb-noun-format"))
                expect(text).not_to(contain("rules injected for"))
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
                expect(dumped).to(contain("hide-inner-details"))
                expect(dumped.strip()).to(equal((result.additional_context or "").strip()))
            finally:
                tmp.cleanup()

    with context("that invokes a handler whose tool has a docstring"):

        with it("should put that description on the hook event as agent_message"):
            @agent_toolset
            class _DescribedFixture:
                @hook("preToolUse")
                def on_pre_tool(self, payload: HookPayload) -> dict:
                    """Honor the hook operation description."""
                    return {"permission": "allow"}

            out = _dispatch({"hook_event_name": "preToolUse"}, toolsets=[_DescribedFixture])
            expect(out["agent_message"]).to(equal("Honor the hook operation description."))
            expect(out["permission"]).to(equal("allow"))

    with context("that invokes a handler returning a status rather than hook fields"):

        with it("should carry the handler through without a dispatch failure"):
            @agent_toolset
            class _StatusFixture:
                @hook("sessionStart")
                def on_session_start(self, payload: HookPayload) -> str:
                    return "running"

            out = _dispatch({"hook_event_name": "sessionStart"}, toolsets=[_StatusFixture])
            expect(out["permission"]).to(equal("allow"))

        with it("should leave the hook event free of an agent message"):
            @agent_toolset
            class _StatusFixture:
                @hook("sessionStart")
                def on_session_start(self, payload: HookPayload) -> str:
                    """Report whether the host already runs."""
                    return "running"

            out = _dispatch({"hook_event_name": "sessionStart"}, toolsets=[_StatusFixture])
            expect(out.get("agent_message")).to(equal(None))

    with context("that parses stdin payloads"):

        with it("should strip a UTF-8 BOM"):
            raw = b'\xef\xbb\xbf{"hook_event_name":"stop"}'
            expect(dict(HookPayload.from_stdin(raw))).to(
                equal({"hook_event_name": "stop"})
            )


def _dispatch_log_folder(root: Path) -> Path:
    """The folder a stop event's dispatch log lands in, for the project at root."""
    HookServer(root, HandlerCatalog([], root)).dispatch(HookPayload({"hook_event_name": "stop"}))
    return next((root / ".sessions").rglob("dispatch.debug")).parent


with description("a project's hook logs") as self:

    with before.each:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.main_logs = (self.root / ".sessions" / "main" / "logs").as_posix()

    with after.each:
        self._tmp.cleanup()

    with context("with no work session open"):

        with it("should go to the main session's logs folder"):
            expect(_dispatch_log_folder(self.root).as_posix()).to(equal(self.main_logs))

    with context("with a work session open"):

        with before.each:
            self.sessions = Sessions(self.root)
            self.sessions.switch("checkout", workpath=self.root)

        with it("should go to that session's logs folder"):
            expect(_dispatch_log_folder(self.root).as_posix()).to(
                equal((self.root / ".sessions" / "checkout" / "logs").as_posix())
            )

        with context("that was closed"):

            with it("should go to the main session's logs folder"):
                self.sessions.close(self.sessions.current())
                expect(_dispatch_log_folder(self.root).as_posix()).to(equal(self.main_logs))

        with context("that was switched to main"):

            with it("should go to the main session's logs folder"):
                self.sessions.switch("main", workpath=self.root)
                expect(_dispatch_log_folder(self.root).as_posix()).to(equal(self.main_logs))


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
                @hook("stop")
                def on_stop(self, payload: HookPayload) -> dict:
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


with description("inject_rules hook dispatch"):

    with context("that receives a Write payload for a sketch markdown path"):

        with it("should inject BDD bags that glob sketches"):
            out = _dispatch(
                {
                    "hook_event_name": "postToolUse",
                    "tool_name": "Write",
                    "tool_input": {
                        "path": "space/kanban/.context/kanban-sketch.md"
                    },
                },
                toolsets=[Bdd()],
            )
            expect(out.get("additional_context") or "").to(equal(""))

        with it("should inject clean engineering bags that glob sketches"):
            out = _dispatch(
                {
                    "hook_event_name": "postToolUse",
                    "tool_name": "Write",
                    "tool_input": {
                        "path": "space/kanban/.context/kanban-sketch.md"
                    },
                },
                toolsets=[CleanEngineering()],
            )
            expect(out.get("additional_context") or "").to(equal(""))

    with context("that receives a sketch action payload with listed BDD"):

        with it("should inject listed BDD rules without a matching path"):
            out = _dispatch(
                {
                    "hook_event_name": "postToolUse",
                    "tool_name": "sketch.sketch",
                    "tool_input": {"guidance": ["cdd_guidance.practices.bdd.bdd:Bdd"]},
                },
                toolsets=[Sketch()],
            )
            expect(out.get("additional_context") or "").to(equal(""))

    with context("that receives an action payload on a toolset that also has rules"):

        with it("should keep listed-guidance inject instead of the collection glob"):
            from types import SimpleNamespace

            from harness.guidance_actions.guidance_actions import GuidanceAction
            from harness.guidance.fixtures.sample_tool.sample_tool_host import (
                SampleGuidance,
            )

            @agent_toolset
            class _ListedInjectAction(GuidanceAction):
                @property
                def rules(self):
                    return SimpleNamespace(
                        inject_rules=lambda payload: {"additional_context": "STOLEN"}
                    )

            out = _dispatch(
                {
                    "hook_event_name": "postToolUse",
                    "tool_name": "_listed_inject_action",
                    "tool_input": {"guidance": [SampleGuidance(format="markdown")]},
                },
                toolsets=[_ListedInjectAction()],
            )
            expect(out.get("additional_context") or "").to(equal(""))


with description("a hook handler"):
    with before.each:
        _PayloadReader.seen = []
        self.root = Path(tempfile.mkdtemp())
        HookServer(self.root, HandlerCatalog([_PayloadReader], self.root)).dispatch(
            HookPayload(
                {
                    "hook_event_name": "postToolUse",
                    "tool_name": "mcp__cdd__generate_generate",
                    "tool_input": json.dumps({"guidance": "stories-story-map"}),
                    "workspace_roots": [str(self.root)],
                }
            )
        )

    with it("should be handed the tool the event is about"):
        expect(_PayloadReader.seen[0].tool_name).to(equal("mcp__cdd__generate_generate"))

    with it("should be handed the tool's arguments, read from the text the IDE sent"):
        expect(_PayloadReader.seen[0].tool_input).to(equal({"guidance": "stories-story-map"}))

    with it("should be handed the project the event happened in"):
        expect(_PayloadReader.seen[0].project).to(equal(self.root))

    with context("with an event Claude Code sent, which names the folder it ran in"):
        with it("should take that folder as the project"):
            expect(HookPayload({"cwd": str(self.root)}).project).to(equal(self.root))

    with it("should be handed the session open in the project the event happened in"):
        expect(_PayloadReader.seen[0].session.session_path).to(equal(self.root.resolve() / ".sessions" / "main"))

    with it("should be handed one session for the whole event"):
        expect(_PayloadReader.seen[0].session).to(be(_PayloadReader.seen[0].session))

    with context("with an event that names no project"):
        with it("should work in the session open in the checkout of the hook server that received it"):
            received = HookPayload({"hook_event_name": "stop"}).received_in(self.root)
            expect(received.session.session_path).to(equal(self.root.resolve() / ".sessions" / "main"))


@agent_toolset
class _ToastingInject:
    @hook("postToolUse")
    def on_used(self, payload: HookPayload) -> dict:
        return {"additional_context": "rules for the edit", "toast": "rules injected for stories-scenarios"}


with description("a hook that gives a toast"):
    with before.each:
        self.shown: list[tuple[str, list[Path]]] = []
        self.root = Path(tempfile.mkdtemp())
        self.registered = HookServer._toast_shown_by
        self.payload = HookPayload({"hook_event_name": "postToolUse", "tool_name": "Write", "workspace_roots": [str(self.root)]})

    with after.each:
        HookServer._toast_shown_by = self.registered
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with a notifier registered to show toasts"):
        with before.each:
            HookServer.show_toasts_with(lambda toast, roots: self.shown.append((toast, roots)))
            self.result = HookServer(self.root, HandlerCatalog([_ToastingInject], self.root)).dispatch(self.payload)

        with it("should have the notifier show the toast in the chat's workspace folders"):
            expect(self.shown).to(equal([("rules injected for stories-scenarios", [self.root])]))

        with it("should not send the toast to the IDE"):
            expect(self.result.as_dict()).to(equal({"permission": "allow", "additional_context": "rules for the edit"}))

    with context("with no notifier registered"):
        with before.each:
            HookServer._toast_shown_by = None

        with it("should still give the IDE the hook's context"):
            result = HookServer(self.root, HandlerCatalog([_ToastingInject], self.root)).dispatch(self.payload)
            expect(result.additional_context).to(equal("rules for the edit"))


with description("hook process helpers"):

    with it("should use python.exe for the Cursor dispatch command so stdout is returned"):
        from harness.hooks.hook_installation import HookInstallation
        from harness.process.process import PythonInterpreter

        install = HookInstallation(IdeLayout("Cursor"), _REPO_ROOT / ".cursor", repo=_REPO_ROOT)
        command = install.dispatch_command.replace("\\", "/")
        python = PythonInterpreter(sys.executable).console.replace("\\", "/")
        expect(command).to(contain(python))
        expect(command).to(contain("harness/hooks/hook_daemon.py"))
        if sys.platform == "win32":
            expect(command).to(contain("python.exe"))
            expect(command).not_to(contain("pythonw.exe"))

    with it("should include CREATE_NO_WINDOW in detached daemon flags on Windows"):
        from harness.process.process import BackgroundStart

        flags = BackgroundStart().creationflags
        if sys.platform == "win32":
            expect(bool(flags & getattr(subprocess, "CREATE_NO_WINDOW", 0))).to(equal(True))
            expect(bool(flags & getattr(subprocess, "DETACHED_PROCESS", 0))).to(equal(False))

    with it("should give one checkout the same daemon port every start"):
        from harness.hooks.hook_daemon import HookDaemon

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            expect(HookDaemon(repo).port).to(equal(HookDaemon(repo).port))


with description("a hook server whose project registers no sessions"):

    with before.each:
        @agent_toolset
        class _ContextInject:
            @hook("postToolUse")
            def on_inject(self, payload: HookPayload) -> dict:
                return {"additional_context": "stories scenario rules"}

        class _Sessionless(HookServer):
            session = property(lambda self: None)

        self.root = Path(tempfile.mkdtemp())
        self.server = _Sessionless(self.root, HandlerCatalog([_ContextInject], self.root))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should answer an event from a chat with its hooks' context"):
        result = self.server.handle_stdin(
            json.dumps({"hook_event_name": "postToolUse", "conversation_id": "chat-a"}).encode()
        )
        expect(result.additional_context).to(equal("stories scenario rules"))

    with it("should answer a prompt from a chat"):
        result = self.server.handle_stdin(
            json.dumps({"hook_event_name": "beforeSubmitPrompt", "conversation_id": "chat-a"}).encode()
        )
        expect(result.permission).to(equal("allow"))


with description("a hook install"):

    with before.each:
        from harness.hooks.hook_installation import HookInstallation

        @agent_toolset
        class _StopHook:
            @hook("stop")
            def on_stop(self, payload: HookPayload) -> dict:
                return {}

        self.folder = Path(tempfile.mkdtemp())
        self.install = HookInstallation(IdeLayout("Cursor"), self.folder, repo=_REPO_ROOT)
        self.tool = _StopHook().tools["on_stop"]

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with the person's own hooks in hooks.json"):

        with before.each:
            (self.folder / "hooks.json").write_text(
                json.dumps({"version": 1, "hooks": {"stop": [{"command": "my-own-hook"}]}}), encoding="utf-8"
            )
            self.install.write(self.tool)

        with it("should keep the person's hook"):
            hooks = json.loads((self.folder / "hooks.json").read_text(encoding="utf-8"))["hooks"]
            expect([item["command"] for item in hooks["stop"]]).to(contain("my-own-hook"))

    with context("with a hooks.json that is not JSON"):

        with before.each:
            self.manifest = self.folder / "hooks.json"
            self.manifest.write_text('{"hooks": {"stop": [{"command": "my-own-hook"}', encoding="utf-8")

        with it("should refuse to install the hook"):
            from harness.hooks.hooks import HooksFileUnreadable

            expect(lambda: self.install.write(self.tool)).to(raise_error(HooksFileUnreadable))

        with it("should leave the person's file as it was"):
            from harness.hooks.hooks import HooksFileUnreadable

            try:
                self.install.write(self.tool)
            except HooksFileUnreadable:
                pass
            expect(self.manifest.read_text(encoding="utf-8")).to(contain("my-own-hook"))


with description("a checkout's hook server"):

    with before.each:
        self.root = Path(tempfile.mkdtemp())

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with hooks installed for Kilo only"):

        with before.each:
            handlers = self.root / IdeLayout("Kilo").folder_name / "hook-handlers.json"
            handlers.parent.mkdir()
            handlers.write_text(
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
                ),
                encoding="utf-8",
            )
            self.server = HookServer.from_repository(RepositoryToolsets(self.root))

        with it("should serve the events the Kilo install registered"):
            expect(self.server.diagnose()["events"]).to(contain("stop"))

        with it("should keep the daemon's address outside every IDE folder"):
            from harness.hooks.hook_daemon import HookDaemon

            expect(HookDaemon(self.root).address_file.path.parent.name).to(equal(".hook-server"))

    with context("with a toolset whose hooks are kept out of install"):

        with before.each:
            @Hooks(deploy=False)
            @agent_toolset
            class _Undeployed:
                @hook("stop")
                def on_stop(self, payload: HookPayload) -> dict:
                    return {"agent_message": "should not run"}

            self.catalog = HandlerCatalog([_Undeployed], self.root)

        with it("should serve none of its events"):
            expect(self.catalog.event_names).to(equal([]))


with description("a hook event that reports a file the agent changed"):

    with context("from Claude Code's edit tool"):
        with it("should report an edit"):
            expect(HookPayload({"hook_event_name": "PostToolUse", "tool_name": "Edit"}).is_edit).to(be_true)

    with context("from Cursor's file-edit event"):
        with it("should report an edit"):
            expect(HookPayload({"hook_event_name": "afterFileEdit"}).is_edit).to(be_true)

    with context("from a tool that only reads"):
        with it("should report no edit"):
            expect(HookPayload({"hook_event_name": "PostToolUse", "tool_name": "Read"}).is_edit).to(equal(False))
