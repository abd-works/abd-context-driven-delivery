"""BDD development specs for session logging — explicit SessionLog.append; no @log."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions", "agents"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("tools", None)
sys.modules.pop("sessions", None)

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from workspace import SessionLog
from tools.tool import _ToolsetRunner, coalesce_run_context
from agents.agent import AgentSession


with description("an action that is expanded"):
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
        expect("role=expansion" in events).to(be_true)
        expect("name=narrate" in events).to(be_true)


with description("a tool that appends a run record"):
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
        expect("role=run" in events).to(be_true)
        expect(self.log.session_name).to(equal("runner-spec"))


with description("a session log that is bound"):
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

    with context("with an append"):
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
            expect(self.log.last_payload is not None).to(be_true)


with description("a tool that does not append"):
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


with description("a session log bound to an agent session"):
    with before.each:
        SessionLog.set_instance(None)
        self.log = SessionLog()
        SessionLog.set_instance(self.log)
        self.root = Path(tempfile.mkdtemp(prefix="session_log_agent_"))
        self.agent_session = AgentSession(
            name="agent-trail",
            folder=self.root / ".agent_sessions" / "agent-trail",
            context_root=self.root,
        )
        self.agent_session.folder.mkdir(parents=True, exist_ok=True)
        self.log.bind(self.agent_session)

    with it("should keep events under eval_log_dir"):
        self.log.append(
            kind="tool",
            toolset="probe",
            name="ping",
            summary="message=hi",
            ok=True,
        )
        events_path = self.agent_session.eval_log_dir / "events.log"
        expect(events_path.is_file()).to(be_true)
        expect("name=ping" in events_path.read_text(encoding="utf-8")).to(be_true)

    with context("with a hanging turn"):
        with it("should mirror append onto the open turn tool calls"):
            turn = self.agent_session.mint_turn(action="validate")
            self.log.append(
                kind="tool",
                toolset="probe",
                name="validate",
                summary="ok",
                ok=True,
                role="run",
            )
            expect(len(turn.tool_calls)).to(equal(1))
            expect(turn.tool_calls[0].name).to(equal("validate"))


with description("a tools run context"):
    with before.each:
        self.sessions_root = Path(tempfile.mkdtemp(prefix="session_log_coalesce_"))
        SessionLog.set_instance(None)
        self.log = SessionLog(sessions_root=self.sessions_root)
        SessionLog.set_instance(self.log)

    with it("should coalesce top-level session into context when context omits it"):
        merged = coalesce_run_context({"path": "agents"}, "judge-session")
        expect(merged["session"]).to(equal("judge-session"))
        expect(merged["path"]).to(equal("agents"))

    with it("should keep an existing context session over top-level session"):
        merged = coalesce_run_context(
            {"path": "agents", "session": "context-wins"},
            "top-level",
        )
        expect(merged["session"]).to(equal("context-wins"))

    with it("should fall back to the bound session log name when both are omitted"):
        self.log.set_session("bound-session")
        merged = coalesce_run_context({"path": "agents"}, None)
        expect(merged["session"]).to(equal("bound-session"))
