"""Mistake turn then correction turn — turn-finish commit not conditional on dirty."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
SKETCH = Path(
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md"
)
ORIGINAL = """      that has finished its turn
        it should record the action run on the session trail
        it should attach the action run record to its turn
        with a dirty working tree on its session branch
          it should commit its scoped changes on the session branch
        it should push its session branch to origin
"""


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()

    bdd.begin_eval_turn()
    eid = bdd.log_mistake(
        artifact=str(SKETCH).replace("\\", "/"),
        rule="nest-by-enabling-events",
        wrong=(
            "Nested commit under `with a dirty working tree on its session branch` at turn finish. "
            "Finishing a turn after work always commits scoped changes — dirty is not an optional `with` branch."
        ),
        original=ORIGINAL,
    )
    bdd.finish_eval_turn(
        prompt="log mistake — turn finish commit not conditional on dirty",
        result=f"entry_id={eid}",
        context=SESSION,
    )

    bdd.begin_eval_turn()
    bdd.log_correction(
        entry_id=eid,
        improved=SKETCH.read_text(encoding="utf-8"),
        how="Remove dirty `with`; commit is direct outcome under that has finished its turn.",
        status="fixed",
    )
    bdd.finish_eval_turn(
        prompt="log correction — turn finish always commits",
        result=f"entry_id={eid} fixed; sketch + workspace_spec.py",
        context=SESSION,
    )


if __name__ == "__main__":
    main()
