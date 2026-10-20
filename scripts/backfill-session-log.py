"""Reparent misrouted session.log lines and append retroactive action lines with chat pointers."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _transcript_line_count(path: Path) -> str:
    if not path.is_file():
        return "1"
    count = len(path.read_text(encoding="utf-8", errors="replace").splitlines()) or 1
    return f"1-{count}" if count > 1 else "1"


def _reparent_no_chat(line: str, chat_id: str, transcript: Path, line_numbers: str) -> str:
    pointer = f"{chat_id} {transcript} {line_numbers}"
    if " no-chat " in line:
        return line.split(" no-chat ", 1)[0] + " " + pointer
    return line


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill space-testing session.log from misrouted sessions.")
    parser.add_argument("--session", default="space-testing")
    parser.add_argument(
        "--from-session",
        action="append",
        default=["satisfy-test", "satisfy-probe"],
        help="Session folder names under .sessions/ whose log lines to reparent.",
    )
    parser.add_argument(
        "--chat-id",
        default="b4c2a422-7199-47ce-9656-c0429af8adb8",
    )
    parser.add_argument(
        "--transcript",
        default=(
            r"C:\Users\jeffa\.cursor\projects\c-dev-abd-context-driven-delivery"
            r"\agent-transcripts\b4c2a422-7199-47ce-9656-c0429af8adb8"
            r"\b4c2a422-7199-47ce-9656-c0429af8adb8.jsonl"
        ),
    )
    args = parser.parse_args()

    from harness.installation.bootstrap import ensure_import_path
    from space.session import Session

    ensure_import_path(_REPO)
    transcript = Path(args.transcript).resolve()
    line_numbers = _transcript_line_count(transcript)
    workpath = _REPO / "space"
    Session._current = None
    Session.switch(args.session, workpath=workpath, repo_path=_REPO)
    session = Session.current()
    if session is None or session.session_path is None:
        raise SystemExit("could not open target session")

    session.note_chat(args.chat_id, transcript, line_numbers)
    session._append_log("--- retroactive backfill")

    reparented: list[str] = []
    for name in args.from_session:
        source = _REPO / ".sessions" / name / "session.log"
        if not source.is_file():
            continue
        for line in source.read_text(encoding="utf-8").splitlines():
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("--- probe"):
                continue
            reparented.append(_reparent_no_chat(cleaned, args.chat_id, transcript, line_numbers))

    log_path = session.session_path / "session.log"
    existing = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    existing_lines = {line.strip() for line in existing.splitlines() if line.strip()}
    new_lines = [line for line in reparented if line not in existing_lines]
    if new_lines:
        with log_path.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write("\n".join(new_lines) + "\n")

    harness = _REPO / "harness" / "agent_tools"
    ce = _REPO / "cdd_guidance" / "practices" / "clean_engineering"
    space_mod = _REPO / "space" / "session"
    retro_paths = [
        harness / "agent_tools_probe.py",
        harness / ".context" / "module-context.md",
        space_mod / "session.py",
        space_mod / "session_probe.py",
        _REPO / "cdd_guidance" / "actions" / "satisfy" / "satisfy.py",
        _REPO / "scripts" / "backfill-session-log.py",
    ]
    for action, paths in (
        ("retroactive", retro_paths),
        ("session-diagnostics", [_REPO / "space" / "session" / "session_probe.py"]),
        ("mark-loop", [space_mod / "session.py"]),
        ("satisfy", [harness, ce]),
        ("validate", [harness / "agent_tools_probe.py"]),
    ):
        session.note_chat(args.chat_id, transcript, line_numbers)
        session.log_action(action, paths)

    print(f"backfilled {len(new_lines)} line(s) into {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
