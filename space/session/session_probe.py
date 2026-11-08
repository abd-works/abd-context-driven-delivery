"""SessionProbe - checks session logging end to end in a throwaway session, for ``SessionDiagnostics.session_diagnostics``."""

from __future__ import annotations

import shutil
import tempfile
import traceback
from pathlib import Path
from typing import Any

from harness.agent_tools.chat_pointer import ChatPointer

_SESSION_PROBE_NAME = "guidance-probe"
# How many of the log's last lines the report shows, enough to see the lines the probe's actions wrote.
_TAIL_LINES = 6


class SessionProbe:
    """One run of the session-log probe: a throwaway repository and session, a generate and a validate run in it, and
    the checks that their log lines name the practice, the workpath, and the probe's chat, and that loops are marked."""

    def __init__(self) -> None:
        self._repo = Path(tempfile.mkdtemp(prefix="cdd-session-probe-"))
        (self._repo / ".git").mkdir()
        self._work = self._repo / "work"
        self._work.mkdir()

    def run(self) -> dict[str, Any]:
        """The probe's result for diagnostics.json: green when every check passed, else red with what failed. A probe's
        job is to report a failure, so one raised while probing is reported red with its trace, not raised."""
        from harness.installation.repository_toolsets import RepositoryToolsets

        RepositoryToolsets.of_running_checkout().ensure_import_path()
        try:
            return self._report(*self._run_actions())
        except Exception as failure:
            trace = traceback.format_exception(type(failure), failure, failure.__traceback__)
            return {"color": "red", "report": f"session log: {type(failure).__name__}: {failure}", "checks": {}, "tail": trace}
        finally:
            shutil.rmtree(self._repo, ignore_errors=True)

    def _run_actions(self):
        """Generate and validate BDD in the probe's session, opened for the probe's own chat, so its log lines point
        there and no other chat's do."""
        from cdd_guidance.actions.generate.generate import Generate
        from cdd_guidance.actions.validate.validate import Validate
        from space.session.sessions import Sessions

        sessions = Sessions(self._repo)
        sessions.switch(_SESSION_PROBE_NAME, self._work)
        session = sessions.current()
        transcript = session.session_path / "chats" / "guidance-probe.md"
        transcript.parent.mkdir(parents=True, exist_ok=True)
        transcript.write_text("guidance diagnostics probe\n", encoding="utf-8")
        chat = ChatPointer("guidance-probe", transcript, "1")
        Generate(session, chat).generate(["bdd"])
        Validate(session, chat).validate(["bdd"])
        return session, transcript

    def _report(self, session, transcript: Path) -> dict[str, Any]:
        log_text = self._log_text(session)
        checks = {
            "generate_line": "generate" in log_text and "bdd" in log_text,
            "workpath_on_line": str(self._work) in log_text,
            "validate_line": "validate" in log_text and "Bdd" in log_text,
            "chat_pointer": "guidance-probe" in log_text and str(transcript) in log_text,
            "loop_markers": self._marks_loops(session),
        }
        failed = [name for name, passed in checks.items() if not passed]
        tail = log_text.splitlines()[-_TAIL_LINES:]
        if failed:
            return {"color": "red", "report": "session log: " + ", ".join(failed), "checks": checks, "tail": tail}
        report = "session log: generate and validate lines include practice and workpath"
        return {"color": "green", "report": report, "checks": checks, "tail": tail}

    def _log_text(self, session) -> str:
        log = session.log.path
        return log.read_text(encoding="utf-8") if log.is_file() else ""

    def _marks_loops(self, session) -> bool:
        session.log.by(None).next_loop()
        session.log.by(None).next_loop()
        text = self._log_text(session)
        return "--- 1" in text and "--- 2" in text
