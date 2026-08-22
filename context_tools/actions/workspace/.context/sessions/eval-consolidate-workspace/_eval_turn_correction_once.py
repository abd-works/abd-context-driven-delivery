"""Log process mistake + correction for eval single-process turn — one invocation."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
WORKFLOW = Path("context_tools/bdd/.context/bdd-grill-sketch-workflow.md")
ORIGINAL = (
    "Use .\\tools.ps1 from repo root. Write _req.yaml, run, delete.\n"
    "(No warning that separate runs orphan log_mistake / log_correction.)"
)


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()
    bdd.begin_eval_turn()
    entry_id = bdd.log_mistake(
        artifact=str(WORKFLOW).replace("\\", "/"),
        rule="eval-turn-single-process",
        wrong=(
            "Ran begin_eval_turn, log_mistake, log_correction, and finish_eval_turn "
            "as separate tools.ps1 run calls. Each process reloads session.yaml only; "
            "mistakes on disk under mistakes/ are not in session._mistakes; "
            "log_correction _find_mistake fails silently; repairs/ not created; "
            "session.yaml turns 99079d1e and 2245e8ec have mistake_ids: []."
        ),
        original=ORIGINAL,
    )
    improved = WORKFLOW.read_text(encoding="utf-8")
    bdd.log_correction(
        entry_id=entry_id,
        improved=improved,
        how=(
            "Added bdd-grill-sketch-workflow.md section Eval turn — single process; "
            "updated repairs/*/improvement.md and grill-answers tick 8 with orphan "
            "turn ids and replay pattern (turn 26ddc97e)."
        ),
        status="fixed",
    )
    turn_id = bdd.finish_eval_turn(
        prompt="log correction — eval turn single-process attachment",
        result=f"workflow + improvement.md + grill-answers; mistake {entry_id}",
        context=SESSION,
    )
    print(f"entry_id={entry_id} turn={turn_id}")


if __name__ == "__main__":
    main()
