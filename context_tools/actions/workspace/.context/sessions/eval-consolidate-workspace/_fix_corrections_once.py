"""One-process replay: hydrate open mistakes and log_correction in same eval turn."""
from __future__ import annotations

import re
from pathlib import Path

from context_tools.bdd.bdd import Bdd
from eval.session import Correction, Mistake

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
SKETCH_REL = (
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/"
    "workspace-bdd-sketch.md"
)

REPLAY = (
    ("745db890", "mistakes/usage-order-behaviors-7"),
    ("db6b3528", "mistakes/nest-by-enabling-events-2"),
)


def _parse_mistake_md(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^- \*\*(\w+):\*\* (.+)$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def _hydrate(session_folder: Path, folder: str, entry_id: str, tool: str, fidelity: str) -> Mistake:
    base = session_folder / folder
    meta = _parse_mistake_md((base / "mistake.md").read_text(encoding="utf-8"))
    assert meta.get("entry_id") == entry_id, (entry_id, meta.get("entry_id"))
    original = (base / "faultyAsset").read_text(encoding="utf-8")
    return Mistake(
        _entry_id=entry_id,
        _artifact=meta.get("artifact", SKETCH_REL),
        _rule=meta.get("rule", ""),
        _wrong=meta.get("wrong", ""),
        _original=original,
        _tool=tool,
        _fidelity=fidelity,
        _correction=Correction(),
        _folder=folder,
        _session_folder=str(session_folder),
    )


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()
    bdd.begin_eval_turn()
    session = bdd.eval
    assert session is not None
    folder = Path(session.workspace.folder)
    improved = (folder / "workspace-bdd-sketch.md").read_text(encoding="utf-8")
    tool = type(bdd).__name__
    fidelity = bdd.fidelity or "behavior"

    for entry_id, mistake_folder in REPLAY:
        mistake = _hydrate(folder, mistake_folder, entry_id, tool, fidelity)
        session._mistakes.append(mistake)
        session.open_turn.add(mistake)
        how = (
            "Single-process log_correction replay; grill tick 8 before sketch; "
            "run audit under that has finished its turn."
            if entry_id == "745db890"
            else "Nest under turn finish for action-run audit; expand under that is asked for its instructions."
        )
        bdd.log_correction(
            entry_id=entry_id,
            improved=improved,
            how=how,
            status="fixed",
        )

    turn_id = bdd.finish_eval_turn(
        prompt="log correction replay — single-process 745db890 db6b3528",
        result="repairs/ with repairedAsset + improvement.md; session.yaml mistake_ids on turn",
        context=SESSION,
    )
    print(f"finish_eval_turn: {turn_id}")


if __name__ == "__main__":
    main()
