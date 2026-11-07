"""Session log probe implementation — used by ``SessionDiagnostics.session_diagnostics``."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

from space.work_state import working_on

_SESSION_PROBE_NAME = "guidance-probe"
_CDD_REPO = Path(__file__).resolve().parents[2]


def probe_session_log() -> dict[str, Any]:
    """Run generate and validate in a temp session; return pass/fail for diagnostics.json."""
    from harness.installation.bootstrap import ensure_import_path

    ensure_import_path(_CDD_REPO)
    repo = Path(tempfile.mkdtemp(prefix="cdd-session-probe-"))
    (repo / ".git").mkdir()
    work = repo / "work"
    work.mkdir()
    # The probe runs inside the one cdd server, so it names its own project and chat for this call only; every other
    # chat's calls keep theirs.
    with working_on(work):
        return _probe_in(repo, work)


def _probe_in(repo: Path, work: Path) -> dict[str, Any]:
    from space.session.chat_pointer import ChatPointer
    from space.session.sessions import Sessions

    try:
        sessions = Sessions(repo)
        sessions.switch(_SESSION_PROBE_NAME, work)
        session = sessions.current()
        chats = session.session_path / "chats"
        chats.mkdir(parents=True, exist_ok=True)
        transcript = chats / "guidance-probe.md"
        transcript.write_text("guidance diagnostics probe\n", encoding="utf-8")

        from cdd_guidance.actions.generate.generate import Generate
        from cdd_guidance.actions.validate.validate import Validate

        with ChatPointer.serving(ChatPointer("guidance-probe", transcript, "1")):
            Generate(sessions.current()).generate(["bdd"])
            Validate(sessions.current()).validate(["bdd"])

        log_path = session.log.path
        log_text = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
        checks = {
            "generate_line": "generate" in log_text and "bdd" in log_text,
            "workpath_on_line": str(work) in log_text,
            "validate_line": "validate" in log_text and "Bdd" in log_text,
            "chat_pointer": "guidance-probe" in log_text and str(transcript) in log_text,
            "loop_markers": _has_loop_markers(session),
        }
        failed = [name for name, ok in checks.items() if not ok]
        tail = log_text.splitlines()[-6:]
        if failed:
            return {
                "color": "red",
                "report": "session log: " + ", ".join(failed),
                "checks": checks,
                "tail": tail,
            }
        return {
            "color": "green",
            "report": "session log: generate and validate lines include practice and workpath",
            "checks": checks,
            "tail": tail,
        }
    except Exception as exc:
        return _fail(_failure_text(exc))
    finally:
        shutil.rmtree(repo, ignore_errors=True)


def _has_loop_markers(session) -> bool:
    session.log.next_loop()
    session.log.next_loop()
    log = session.log.path
    text = log.read_text(encoding="utf-8") if log.is_file() else ""
    return "--- 1" in text and "--- 2" in text


def _fail(message: str) -> dict[str, object]:
    return {"color": "red", "report": f"session log: {message}", "checks": {}, "tail": []}


def _failure_text(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"
