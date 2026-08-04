"""BDD development specs for session logging - usage order; describes are conditions, not hubs."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("sessions", None)

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from tools.examples.logged_probe import LoggedProbe
from sessions import SessionLog, is_logged, member_is_logged
from tools.tool import _ToolsetRunner


with description("an action that is annotated with log"):
    with it("should be recognized as logged"):
        expect(is_logged(LoggedProbe.ping)).to(be_true)

    with context("that is overriding a base action that is annotated with log"):
        with it("should still be recognized as logged"):
            from context_tools.base.base_context_tool import BaseContextTool
            from context_tools.bdd.bdd import Bdd

            expect(is_logged(BaseContextTool.generate)).to(be_true)
            expect(member_is_logged(Bdd, "generate")).to(be_true)

    with context("that is invoked"):
        with before.each:
            self.sessions_root = Path(tempfile.mkdtemp(prefix="session_log_invoke_"))
            SessionLog.set_instance(None)
            self.log = SessionLog(sessions_root=self.sessions_root)
            SessionLog.set_instance(self.log)
            self.runner = _ToolsetRunner.instance()

        with it("should record a run event on the session trail"):
            response = self.runner.run_request(
                {
                    "toolset": "tools.examples.logged_probe:LoggedProbe",
                    "session": "runner-spec",
                    "tool": "ping",
                    "arguments": {"message": "hi"},
                    "include_resources": False,
                }
            )
            expect(response["ok"]).to(be_true)
            events = (self.log.log_dir / "events.log").read_text(encoding="utf-8")
            expect("name=ping" in events).to(be_true)
            expect(self.log.session_name).to(equal("runner-spec"))

    with context("that is expanded"):
        with before.each:
            self.sessions_root = Path(tempfile.mkdtemp(prefix="session_log_expand_"))
            SessionLog.set_instance(None)
            self.log = SessionLog(sessions_root=self.sessions_root)
            SessionLog.set_instance(self.log)
            self.runner = _ToolsetRunner.instance()

        with it("should record an expansion event on the session trail"):
            response = self.runner.run_request(
                {
                    "toolset": "tools.examples.logged_probe:LoggedProbe",
                    "session": "expand-spec",
                    "action": "narrate",
                    "arguments": {"message": "hi"},
                    "include_resources": False,
                }
            )
            expect(response["ok"]).to(be_true)
            events = (self.log.log_dir / "events.log").read_text(encoding="utf-8")
            expect("kind=expansion" in events).to(be_true)
            expect("name=narrate" in events).to(be_true)

    with context("that has been logged"):
        with before.each:
            self.sessions_root = Path(tempfile.mkdtemp(prefix="session_log_trail_"))
            SessionLog.set_instance(None)
            self.log = SessionLog(sessions_root=self.sessions_root)
            SessionLog.set_instance(self.log)

        with context("with no session name given"):
            with it("should use the default session"):
                self.log.set_session(None)
                expect(self.log.session_name).to(equal("default"))
                expect(self.log.log_dir.name).to(equal("default"))

        with context("with a given session name"):
            with it("should keep events under that session"):
                self.log.set_session("debug-run")
                expect(self.log.session_name).to(equal("debug-run"))
                expect(self.log.log_dir.name).to(equal("debug-run"))

        with context("with verbose off"):
            with it("should write a summary line and keep the last payload"):
                self.log.set_session("spec")
                self.log.append(
                    kind="tool",
                    toolset="probe",
                    name="ping",
                    summary="message=hi",
                    ok=True,
                    payload={"request": {"message": "hi"}, "response": {"result": "pong:hi"}},
                )
                events = (self.log.log_dir / "events.log").read_text(encoding="utf-8")
                expect("kind=tool" in events).to(be_true)
                expect("name=ping" in events).to(be_true)
                expect(list(self.log.log_dir.glob("event-*-request.yaml"))).to(equal([]))
                expect(self.log.last_payload is not None).to(be_true)

            with context("with full logging requested"):
                with it("should flush the last payload"):
                    self.log.set_session("spec")
                    self.log.append(
                        kind="tool",
                        toolset="probe",
                        name="ping",
                        summary="message=hi",
                        ok=True,
                        payload={"request": {"message": "hi"}, "response": {"result": "pong:hi"}},
                    )
                    self.log.apply_log_control("full")
                    expect(self.log.verbose).to(be_true)
                    reqs = list(self.log.log_dir.glob("event-*-request.yaml"))
                    expect(len(reqs)).to(equal(1))
                    expect("hi" in reqs[0].read_text(encoding="utf-8")).to(be_true)

        with context("with verbose on"):
            with it("should write payload files for later events"):
                self.log.set_session("spec")
                self.log.apply_log_control("verbose")
                self.log.append(
                    kind="tool",
                    toolset="probe",
                    name="ping",
                    summary="message=yo",
                    ok=True,
                    payload={"request": {"message": "yo"}, "response": {"result": "pong:yo"}},
                )
                expect(len(list(self.log.log_dir.glob("event-*-request.yaml")))).to(equal(1))
                expect(len(list(self.log.log_dir.glob("event-*-response.yaml")))).to(equal(1))


with description("an action that is not annotated"):
    with it("should not be recognized as logged"):
        expect(is_logged(LoggedProbe.quiet)).to(be_false)

    with context("that is invoked"):
        with before.each:
            self.sessions_root = Path(tempfile.mkdtemp(prefix="session_log_quiet_"))
            SessionLog.set_instance(None)
            self.log = SessionLog(sessions_root=self.sessions_root)
            SessionLog.set_instance(self.log)
            self.runner = _ToolsetRunner.instance()

        with it("should leave the session trail empty"):
            self.runner.run_request(
                {
                    "toolset": "tools.examples.logged_probe:LoggedProbe",
                    "session": "quiet-spec",
                    "tool": "quiet",
                    "arguments": {},
                    "include_resources": False,
                }
            )
            events_path = self.log.log_dir / "events.log"
            expect(events_path.exists()).to(be_false)
