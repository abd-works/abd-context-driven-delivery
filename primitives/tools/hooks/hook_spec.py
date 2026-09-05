# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD development specs for the Hook annotation and HookHarness."""
import sys
import json
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives",):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)

from expects import contain, equal, have_key, raise_error, expect
from mamba import context, description, it

from tools.hooks.hook import Hook, HookHarness


# ---------------------------------------------------------------------------
# Fixture — one handler per Cursor event, registered via @Hook
# ---------------------------------------------------------------------------

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


def _registered_events() -> list[str]:
    return [e["event"] for e in Hook.registered()]


# ---------------------------------------------------------------------------
# Specs
# ---------------------------------------------------------------------------

with description("an operation method annotated with a Cursor event"):

    with context("that is decorated with sessionStart"):
        with it("should carry the sessionStart event name"):
            fn = _Fixture.on_session_start
            expect(fn._hook_event).to(equal("sessionStart"))

        with it("should appear in the hook registry"):
            expect(_registered_events()).to(contain("sessionStart"))

        with it("should fire a notification when invoked"):
            # Arrange
            notified: list[str] = []
            @Hook(event="sessionStart", notify=True, notifier=notified.append)
            def _on(payload: dict) -> dict:
                return {}
            # Act
            _on({})
            # Assert
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
            # Arrange
            registry = [
                {
                    "event": "sessionStart",
                    "handler": lambda p: {},
                    "matcher": None,
                    "timeout": 10,
                    "fail_closed": False,
                }
            ]
            harness = HookHarness(script="primitives/hooks/my_hooks.py")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "hooks.json"
                # Act
                harness.deploy(dest, registry=registry)
                # Assert
                data = json.loads(dest.read_text(encoding="utf-8"))
                expect(data["hooks"]).to(have_key("sessionStart"))

    with context("that deploys a preToolUse handler with a matcher"):
        with it("should include the matcher in the hooks.json entry"):
            # Arrange
            registry = [
                {
                    "event": "preToolUse",
                    "handler": lambda p: {},
                    "matcher": "Write|StrReplace",
                    "timeout": 10,
                    "fail_closed": False,
                }
            ]
            harness = HookHarness(script="primitives/hooks/my_hooks.py")
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "hooks.json"
                # Act
                harness.deploy(dest, registry=registry)
                # Assert
                data = json.loads(dest.read_text(encoding="utf-8"))
                hook_entry = data["hooks"]["preToolUse"][0]
                expect(hook_entry["matcher"]).to(equal("Write|StrReplace"))
