"""Correction turn only — mistake 1c9526fa grill-answers tick 9."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
GRILL = Path(
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md"
)
ENTRY_ID = "1c9526fa"


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()
    bdd.begin_eval_turn()
    bdd.log_correction(
        entry_id=ENTRY_ID,
        improved=GRILL.read_text(encoding="utf-8"),
        how=(
            "Replace slice-boundary grill with BDD design-tree root: highest-level event/state "
            "under that has a turn open; tick 10 will drill substates and legitimate tests."
        ),
        status="fixed",
    )
    bdd.finish_eval_turn(
        prompt="log correction — grill tick 9 design-tree question",
        result=f"entry_id={ENTRY_ID} fixed",
        context=SESSION,
    )


if __name__ == "__main__":
    main()
