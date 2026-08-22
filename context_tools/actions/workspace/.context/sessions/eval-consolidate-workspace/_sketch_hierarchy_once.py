"""Mistake turn then correction turn — inverted subject/entry hierarchy in sketch."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
SKETCH = Path(
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md"
)
EVAL_SKETCH = Path(
    "context_tools/actions/eval/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md"
)
ORIGINAL = """a context tool
  that has an action run against it
    with a workspace
      with a new work session name
"""


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()

    bdd.begin_eval_turn()
    eid = bdd.log_mistake(
        artifact=str(SKETCH).replace("\\", "/"),
        rule="usage-order-behaviors",
        wrong=(
            "Nested enabling event `that has an action run against it` before standing "
            "`with a workspace`. Grill tick 8: subject `a context tool` → standing "
            "`with a workspace` → domain entry event — not event-before-standing."
        ),
        original=ORIGINAL,
    )
    bdd.finish_eval_turn(
        prompt="log mistake — sketch entry hierarchy inverted",
        result=f"entry_id={eid}",
        context=SESSION,
    )

    fixed = SKETCH.read_text(encoding="utf-8")
    SKETCH.write_text(fixed, encoding="utf-8")
    EVAL_SKETCH.write_text(fixed, encoding="utf-8")

    bdd.begin_eval_turn()
    bdd.log_correction(
        entry_id=eid,
        improved=fixed,
        how="Restore tick 8 order: with a workspace before that has an action run against it; sync eval copy.",
        status="fixed",
    )
    bdd.finish_eval_turn(
        prompt="log correction — sketch entry hierarchy",
        result=f"entry_id={eid} fixed",
        context=SESSION,
    )


if __name__ == "__main__":
    main()
