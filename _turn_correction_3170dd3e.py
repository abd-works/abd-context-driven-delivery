"""Correction turn only — mistake 3170dd3e (sketch entry hierarchy). One process."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
SKETCH = Path(
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md"
)
ENTRY_ID = "3170dd3e"


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()
    bdd.begin_eval_turn()
    bdd.log_correction(
        entry_id=ENTRY_ID,
        improved=SKETCH.read_text(encoding="utf-8"),
        how=(
            "OO §2 three levels: BaseContextTool composes Workspace (with a workspace) "
            "before action-run envelope; §4 openWorkSession + Turn.open then agent work. "
            "Design cites workspace-eval-oo-sketch.md only."
        ),
        status="fixed",
    )
    bdd.finish_eval_turn(
        prompt="log correction — sketch hierarchy per OO §2",
        result=f"entry_id={ENTRY_ID} fixed",
        context=SESSION,
    )


if __name__ == "__main__":
    main()
