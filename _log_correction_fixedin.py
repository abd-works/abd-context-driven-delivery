"""log_correction + finish_eval_turn for 54f63ba8 in one session process."""
from __future__ import annotations

import re
from pathlib import Path

from context_tools.clean_engineering.clean_engineering import CleanEngineering
from eval.session import Mistake, ToolCall

ROOT = Path(__file__).resolve().parent
SESSION_FOLDER = ROOT / "context_tools/actions/eval/.context/sessions/eval-consolidate-workspace"
ENTRY_ID = "54f63ba8"
HOW = (
    "Manual draw.io edit — added Correction→Turn association edge (id=21) "
    "for fixedIn; routes via x=1040 to Turn entry."
)

FIELD = re.compile(r"^\-\s+\*\*(?P<key>[^:]+):\*\*\s+(?P<val>.+)$")


def parse_mistake_md(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = FIELD.match(line.strip())
        if m:
            out[m.group("key")] = m.group("val").strip()
    return out


def ensure_mistake(session, entry_id: str) -> Mistake | None:
    found = session._find_mistake(entry_id)
    if found is not None:
        return found
    md_path = SESSION_FOLDER / "mistakes" / "draw-association-for-caller-not-only-owner" / "mistake.md"
    if not md_path.is_file():
        return None
    fields = parse_mistake_md(md_path.read_text(encoding="utf-8"))
    faulty = (md_path.parent / "faultyAsset").read_text(encoding="utf-8")
    mistake = Mistake(
        _entry_id=entry_id,
        _artifact=fields.get("artifact", ""),
        _rule=fields.get("rule", ""),
        _wrong=fields.get("wrong", ""),
        _original=faulty,
        _tool="CleanEngineering",
        _fidelity="model",
        _folder="mistakes/draw-association-for-caller-not-only-owner",
        _session_folder=str(SESSION_FOLDER),
    )
    turn = session.begin_turn()
    session._mistakes.append(mistake)
    turn._mistakes.append(mistake)
    return mistake


def main() -> int:
    ce = CleanEngineering(fidelity="model", path="context_tools/actions/eval", session="eval-consolidate-workspace")
    session = ce.eval
    repairer = ce.repairer

    if ensure_mistake(session, ENTRY_ID) is None:
        print(f"MISSING {ENTRY_ID}")
        return 1

    session.record_tool_call(
        ToolCall(
            _toolset="context_tools.clean_engineering.clean_engineering:CleanEngineering",
            _name="log_correction",
            _summary=f"entry_id={ENTRY_ID}, status=fixed",
        )
    )
    result = repairer.log_correction(entry_id=ENTRY_ID, improved="", how=HOW, status="fixed")
    print(f"log_correction ok {result}")

    closed = session.finish_turn(
        prompt="log correction — Correction→Turn fixedIn edge",
        result=f"closed mistake {ENTRY_ID}; Correction→Turn association in drawio",
        context="eval-consolidate-workspace",
    )
    print(f"finish_turn ok {closed.id if closed else 'no-commit'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
