# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD specs for @hook, HookHarness, and dispatch."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "primitives/hooks"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("hooks", None)

from expects import contain, equal, expect, have_key, raise_error
from mamba import context, description, it
from tools.tool import toolset

from hooks.deploy import HookBinding
from hooks.dispatch import dispatch, parse_payload
from hooks.hook import Hook, HookHarness, hook


class _Fixture:
    @Hook(event="sessionStart")
    def on_session_start(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="beforeSubmitPrompt")
    def on_before_submit_prompt(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="afterAgentResponse")
    def on_after_agent_response(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="afterAgentThought")
    def on_after_agent_thought(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="stop")
    def on_stop(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="sessionEnd")
    def on_session_end(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="preCompact")
    def on_pre_compact(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="preToolUse")
    def on_pre_tool_use(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="postToolUse")
    def on_post_tool_use(self, payload: dict) -> dict:
        return {"permission": "allow"}

    @Hook(event="postToolUseFailure")
    def on_post_tool_use_failure(self, payload: dict) -> dict:
        return {"permission": "allow"}


@toolset
class _DispatchFixture:
    calls: list[str] = []

    @hook(event="afterAgentResponse")
    def on_after(self, payload: dict) -> dict:
        type(self).calls.append("after")
        return {"agent_message": "ran"}


def _registered_events() -> list[str]:
    return [e["event"] for e in Hook.registered()]


with description("an operation method annotated with a Cursor event"):

    with context("that is decorated with sessionStart"):
        with it("should carry the sessionStart event name"):
            fn = _Fixture.on_session_start
            expect(fn._hook_event).to(equal("sessionStart"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("sessionStart"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="sessionStart", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["sessionStart"]))

    with context("that is decorated with beforeSubmitPrompt"):
        with it("should carry the beforeSubmitPrompt event name"):
            fn = _Fixture.on_before_submit_prompt
            expect(fn._hook_event).to(equal("beforeSubmitPrompt"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("beforeSubmitPrompt"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="beforeSubmitPrompt", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["beforeSubmitPrompt"]))

    with context("that is decorated with afterAgentResponse"):
        with it("should carry the afterAgentResponse event name"):
            fn = _Fixture.on_after_agent_response
            expect(fn._hook_event).to(equal("afterAgentResponse"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("afterAgentResponse"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="afterAgentResponse", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["afterAgentResponse"]))

    with context("that is decorated with afterAgentThought"):
        with it("should carry the afterAgentThought event name"):
            fn = _Fixture.on_after_agent_thought
            expect(fn._hook_event).to(equal("afterAgentThought"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("afterAgentThought"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="afterAgentThought", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["afterAgentThought"]))

    with context("that is decorated with stop"):
        with it("should carry the stop event name"):
            fn = _Fixture.on_stop
            expect(fn._hook_event).to(equal("stop"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("stop"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="stop", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["stop"]))

    with context("that is decorated with sessionEnd"):
        with it("should carry the sessionEnd event name"):
            fn = _Fixture.on_session_end
            expect(fn._hook_event).to(equal("sessionEnd"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("sessionEnd"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="sessionEnd", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["sessionEnd"]))

    with context("that is decorated with preCompact"):
        with it("should carry the preCompact event name"):
            fn = _Fixture.on_pre_compact
            expect(fn._hook_event).to(equal("preCompact"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("preCompact"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="preCompact", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["preCompact"]))

    with context("that is decorated with preToolUse"):
        with it("should carry the preToolUse event name"):
            fn = _Fixture.on_pre_tool_use
            expect(fn._hook_event).to(equal("preToolUse"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("preToolUse"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="preToolUse", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["preToolUse"]))

    with context("that is decorated with postToolUse"):
        with it("should carry the postToolUse event name"):
            fn = _Fixture.on_post_tool_use
            expect(fn._hook_event).to(equal("postToolUse"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("postToolUse"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="postToolUse", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["postToolUse"]))

    with context("that is decorated with postToolUseFailure"):
        with it("should carry the postToolUseFailure event name"):
            fn = _Fixture.on_post_tool_use_failure
            expect(fn._hook_event).to(equal("postToolUseFailure"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("postToolUseFailure"))

        with it("should fire a notification when invoked"):
            notified: list[str] = []
            @Hook(event="postToolUseFailure", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            _on({})
            expect(notified).to(equal(["postToolUseFailure"]))

    with context("that is decorated with an unrecognised event"):
        with it("should raise ValueError"):
            def bad_decoration():
                @Hook(event="notAnEvent")
                def fn(self, payload: dict) -> dict:
                    return {}
            expect(bad_decoration).to(raise_error(ValueError))


with description("a hook harness"):

    with context("that deploys a sessionStart handler"):
        with it("should write a sessionStart entry to hooks.json"):
            registry = [
                {
                    "event": "sessionStart",
                    "handler": lambda p: {},
                    "matcher": None,
                    "timeout": 10,
                    "fail_closed": False,
                }
            ]
            harness = HookHarness(script="primitives/hooks/dispatch.py")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "hooks.json"
                harness.deploy(dest, registry=registry)
                data = json.loads(dest.read_text(encoding="utf-8"))
                expect(data["hooks"]).to(have_key("sessionStart"))

    with context("that deploys a preToolUse handler with a matcher"):
        with it("should include the matcher in the hooks.json entry"):
            registry = [
                {
                    "event": "preToolUse",
                    "handler": lambda p: {},
                    "matcher": "Write|StrReplace",
                    "timeout": 10,
                    "fail_closed": False,
                }
            ]
            harness = HookHarness(script="primitives/hooks/dispatch.py")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "hooks.json"
                harness.deploy(dest, registry=registry)
                data = json.loads(dest.read_text(encoding="utf-8"))
                hook_entry = data["hooks"]["preToolUse"][0]
                expect(hook_entry["matcher"]).to(equal("Write|StrReplace"))

    with context("that syncs dispatch entries"):
        with it("should drop dispatch wiring for events not in the target set"):
            harness = HookHarness(script="primitives/hooks/dispatch.py")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "hooks.json"
                dest.write_text(
                    json.dumps(
                        {
                            "version": 1,
                            "hooks": {
                                "beforeSubmitPrompt": [
                                    {
                                        "command": ".venv/Scripts/python.exe primitives/hooks/prompt_log.py",
                                        "timeout": 10,
                                        "failClosed": False,
                                    },
                                    {
                                        "command": ".venv/Scripts/python.exe primitives/hooks/dispatch.py",
                                        "timeout": 30,
                                        "failClosed": False,
                                    },
                                ],
                                "afterAgentResponse": [
                                    {
                                        "command": ".venv/Scripts/python.exe primitives/hooks/dispatch.py",
                                        "timeout": 30,
                                        "failClosed": False,
                                    },
                                ],
                            },
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                harness.sync_dispatch(dest, {"beforeSubmitPrompt"})
                data = json.loads(dest.read_text(encoding="utf-8"))
                expect(data["hooks"]).to(have_key("beforeSubmitPrompt"))
                expect(data["hooks"]).not_to(have_key("afterAgentResponse"))
                before = data["hooks"]["beforeSubmitPrompt"]
                expect(len(before)).to(equal(2))
                expect(before[0]["command"]).to(contain("prompt_log.py"))
                expect(before[1]["command"]).to(contain("dispatch.py"))

        with it("should remove all dispatch wiring when the target set is empty"):
            harness = HookHarness(script="primitives/hooks/dispatch.py")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "hooks.json"
                dest.write_text(
                    json.dumps(
                        {
                            "version": 1,
                            "hooks": {
                                "afterAgentResponse": [
                                    {
                                        "command": ".venv/Scripts/python.exe primitives/hooks/dispatch.py",
                                        "timeout": 30,
                                        "failClosed": False,
                                    },
                                ],
                            },
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                harness.sync_dispatch(dest, set())
                data = json.loads(dest.read_text(encoding="utf-8"))
                expect(data["hooks"]).to(equal({}))


with description("hook dispatch"):

    with context("that receives an afterAgentResponse payload"):

        with it("should skip handlers when the toggle flag is absent"):
            Hook.clear()
            _DispatchFixture.calls = []
            Hook.attach_owners(_DispatchFixture)
            Hook.set_enabled(_DispatchFixture, "on_after", "afterAgentResponse", enabled=False)
            out = dispatch({"hook_event_name": "afterAgentResponse"})
            expect(out).to(equal({"permission": "allow"}))
            expect(_DispatchFixture.calls).to(equal([]))

        with it("should invoke enabled handlers"):
            Hook.clear()
            _DispatchFixture.calls = []
            Hook.attach_owners(_DispatchFixture)
            Hook.set_enabled(_DispatchFixture, "on_after", "afterAgentResponse", enabled=True)
            try:
                out = dispatch({"hook_event_name": "afterAgentResponse"})
                expect(out["permission"]).to(equal("allow"))
                expect(out["agent_message"]).to(equal("ran"))
                expect(_DispatchFixture.calls).to(equal(["after"]))
            finally:
                Hook.set_enabled(_DispatchFixture, "on_after", "afterAgentResponse", enabled=False)

    with context("that parses stdin payloads"):

        with it("should strip a UTF-8 BOM"):
            raw = b'\xef\xbb\xbf{"hook_event_name":"stop"}'
            expect(parse_payload(raw)).to(equal({"hook_event_name": "stop"}))


with description("a hook binding"):

    with context("that exposes skill sources"):
        with it("should include instructions and flag path for on and off"):
            binding = HookBinding(
                event="beforeSubmitPrompt",
                operation="auto_turn",
                slug="turn",
                owner="Turn",
                folder="utilities/turn",
            )
            payloads = binding.skill_sources()
            expect(len(payloads)).to(equal(2))
            on_payload = payloads[0]
            expect(on_payload["name"]).to(equal("auto_turn_before_submit_prompt_on"))
            expect(on_payload["body"]).to(contain("`auto_turn`"))
            expect(on_payload["body"]).to(
                contain(".context/hooks/turn/auto_turn_before_submit_prompt.enabled")
            )
