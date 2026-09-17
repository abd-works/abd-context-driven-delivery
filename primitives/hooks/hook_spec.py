"""BDD specs for installer @hook dispatch."""
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

from expects import be_true, equal, expect
from mamba import context, description, it
from agent_tools import agent_toolset

from hooks.dispatch import dispatch, parse_payload, set_enabled
from installer.marks import hook


@agent_toolset
class _DispatchFixture:
    calls: list[str] = []

    @hook("afterAgentResponse")
    def on_after(self, payload: dict) -> dict:
        type(self).calls.append("after")
        return {"agent_message": "ran"}


@agent_toolset
class _StopFixture:
    calls: list[str] = []

    @hook("stop")
    def on_stop(self, payload: dict) -> dict:
        type(self).calls.append("stop")
        return {"followup_message": "/turn"}


with description("hook dispatch"):

    with context("that receives an afterAgentResponse payload"):

        with it("should skip handlers when the toggle flag is absent"):
            _DispatchFixture.calls = []
            set_enabled(_DispatchFixture, "on_after", "afterAgentResponse", enabled=False)
            out = dispatch(
                {"hook_event_name": "afterAgentResponse"},
                hosts=[_DispatchFixture],
            )
            expect(out).to(equal({"permission": "allow"}))
            expect(_DispatchFixture.calls).to(equal([]))

        with it("should invoke enabled handlers"):
            _DispatchFixture.calls = []
            set_enabled(_DispatchFixture, "on_after", "afterAgentResponse", enabled=True)
            try:
                out = dispatch(
                    {"hook_event_name": "afterAgentResponse"},
                    hosts=[_DispatchFixture],
                )
                expect(out["permission"]).to(equal("allow"))
                expect(out["agent_message"]).to(equal("ran"))
                expect(_DispatchFixture.calls).to(equal(["after"]))
            finally:
                set_enabled(
                    _DispatchFixture, "on_after", "afterAgentResponse", enabled=False
                )

    with context("that receives a stop payload"):

        with it("should pass through followup_message from enabled handlers"):
            _StopFixture.calls = []
            set_enabled(_StopFixture, "on_stop", "stop", enabled=True)
            try:
                out = dispatch({"hook_event_name": "stop"}, hosts=[_StopFixture])
                expect(out).to(equal({"permission": "allow", "followup_message": "/turn"}))
                expect(_StopFixture.calls).to(equal(["stop"]))
            finally:
                set_enabled(_StopFixture, "on_stop", "stop", enabled=False)

        with it("should keep user_message separate from agent_message"):
            @agent_toolset
            class _MessageFixture:
                @hook("beforeSubmitPrompt")
                def on_before(self, payload: dict) -> dict:
                    return {
                        "user_message": "for user",
                        "agent_message": "for agent",
                    }

            set_enabled(_MessageFixture, "on_before", "beforeSubmitPrompt", enabled=True)
            try:
                out = dispatch(
                    {"hook_event_name": "beforeSubmitPrompt"},
                    hosts=[_MessageFixture],
                )
                expect(out["user_message"]).to(equal("for user"))
                expect(out["agent_message"]).to(equal("for agent"))
            finally:
                set_enabled(
                    _MessageFixture, "on_before", "beforeSubmitPrompt", enabled=False
                )

    with context("that parses stdin payloads"):

        with it("should strip a UTF-8 BOM"):
            raw = b'\xef\xbb\xbf{"hook_event_name":"stop"}'
            expect(parse_payload(raw)).to(equal({"hook_event_name": "stop"}))


with description("session hook logs"):

    with context("when no work session is active"):

        with it("should create default session logs under .sessions/default/logs"):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                from hooks.session_logs import ensure_default_session, session_log_path

                folder = ensure_default_session(root)
                expect(folder.is_dir()).to(be_true)
                log = session_log_path(root, "prompt-log.txt")
                expect(log.parent.as_posix()).to(
                    equal((root / ".sessions/default/logs").as_posix())
                )
                log.write_text("probe\n", encoding="utf-8")
                expect(log.is_file()).to(be_true)
                expect((folder / "session.md").is_file()).to(be_true)
