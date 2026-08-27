"""Mistake turn then correction turn — inverted subject/entry hierarchy in sketch."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
SKETCH = Path(
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md"
)
ORIGINAL = """a context tool
  that has an action run against it
    with a workspace
      with a new work session name
"""


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.workspace.open(bdd)
    bdd.begin_turn(action="mistake")
    eid = bdd.record_mistake(
        artifact=str(SKETCH).replace("\\", "/"),
        rule="usage-order-behaviors",
        wrong=(
            "Nested enabling event `that has an action run against it` before standing "
            "`with a workspace`. Grill tick 8: subject `a context tool` → standing "
            "`with a workspace` → domain entry event — not event-before-standing."
        ),
        original=ORIGINAL,
        introducing_commit=bdd.workspace.current_work_session.git.current_commit,
    )
    bdd.finish_turn(
        prompt="log mistake — sketch entry hierarchy inverted",
        result=f"entry_id={eid}",
        context=SESSION,
    )

    fixed = SKETCH.read_text(encoding="utf-8")

    bdd.begin_turn(action="correction")
    bdd.record_correction(
        entry_id=eid,
        improved=fixed,
        how="Restore tick 8 order: with a workspace before that has an action run against it.",
        status="fixed",
    )
    bdd.finish_turn(
        prompt="log correction — sketch entry hierarchy",
        result=f"entry_id={eid} fixed",
        context=SESSION,
    )


if __name__ == "__main__":
    main()
