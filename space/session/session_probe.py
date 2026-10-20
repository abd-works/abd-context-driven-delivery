"""Session log probe implementation — used by ``SessionDiagnostics.session_diagnostics``."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

_SESSION_PROBE_NAME = "guidance-probe"
_CDD_REPO = Path(__file__).resolve().parents[2]


def probe_session_log() -> dict[str, Any]:
    """Run generate and validate in a temp session; return pass/fail for diagnostics.json."""
    from harness.installation.bootstrap import ensure_import_path

    ensure_import_path(_CDD_REPO)
    prior_repo = os.environ.get("CDD_REPO")
    prior_project = os.environ.get("CDD_PROJECT")
    repo = Path(tempfile.mkdtemp(prefix="cdd-session-probe-"))
    try:
        (repo / ".git").mkdir()
        work = repo / "work"
        work.mkdir()
        os.environ["CDD_REPO"] = str(repo)
        os.environ["CDD_PROJECT"] = str(work)
        from space.session import Session

        Session._current = None
        Session.new(_SESSION_PROBE_NAME, work, repo)
        session = Session.current()
        chats = session.session_path / "chats"
        chats.mkdir(parents=True, exist_ok=True)
        transcript = chats / "guidance-probe.md"
        transcript.write_text("guidance diagnostics probe\n", encoding="utf-8")
        os.environ["CDD_CONVERSATION_ID"] = "guidance-probe"
        os.environ["CDD_TRANSCRIPT_PATH"] = str(transcript)
        os.environ["CDD_TRANSCRIPT_LINES"] = "1"
        Session._current = None

        from generate.generate import Generate
        from validate.validate import Validate

        Generate().generate(["bdd"])
        Validate().validate(["bdd"])

        session = Session.current()
        if session is None or session.session_path is None:
            return _fail("no session bound after generate/validate")

        log_path = session.session_path / "session.log"
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
        from space.session import Session

        if prior_repo is None:
            os.environ.pop("CDD_REPO", None)
        else:
            os.environ["CDD_REPO"] = prior_repo
        if prior_project is None:
            os.environ.pop("CDD_PROJECT", None)
        else:
            os.environ["CDD_PROJECT"] = prior_project
        Session._current = None
        shutil.rmtree(repo, ignore_errors=True)


def _has_loop_markers(session) -> bool:
    session.loop()
    session.loop()
    log = session.session_path / "session.log"
    text = log.read_text(encoding="utf-8") if log.is_file() else ""
    return "--- 1" in text and "--- 2" in text


def _fail(message: str) -> dict[str, object]:
    return {"color": "red", "report": f"session log: {message}", "checks": {}, "tail": []}


def _failure_text(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"
