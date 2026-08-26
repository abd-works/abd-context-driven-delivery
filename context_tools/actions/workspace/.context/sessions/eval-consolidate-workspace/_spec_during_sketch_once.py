"""Mistake turn then correction turn — hand-edited spec during sketch phase."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
SPEC = Path("context_tools/actions/workspace/workspace_spec.py")
ORIGINAL = """            with context("that the agent is finished working with it"):
                with it("should finish its turn for the action"):
                    # BDD: SIGNATURE
                    pass

            with context("that has finished its turn"):
"""


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.workspace.open(bdd)
    bdd.begin_turn(action="mistake")
    eid = bdd.record_mistake(
        artifact=str(SPEC).replace("\\", "/"),
        rule="usage-order-behaviors",
        wrong=(
            "Hand-edited workspace_spec.py while the consolidated sketch is still in grill/sketch. "
            "bdd-grill-sketch-workflow.md: {module}_spec.py only after sketch is judge-clean and "
            "iterate unlocks generate — not during grill/sketch turns. Agent-finish slice belongs "
            "in workspace-bdd-sketch.md only until generate."
        ),
        original=ORIGINAL,
        introducing_commit=bdd.workspace.current_work_session.git.current_commit,
    )
    bdd.finish_turn(
        prompt="log mistake — spec edited during sketch phase",
        result=f"entry_id={eid}",
        context=SESSION,
    )

    bdd.begin_turn(action="correction")
    bdd.record_correction(
        entry_id=eid,
        improved=SPEC.read_text(encoding="utf-8"),
        how="Revert premature spec edit; agent-finish slice stays in sketch until validate + generate.",
        status="fixed",
    )
    bdd.finish_turn(
        prompt="log correction — spec reverted; sketch-only until generate",
        result=f"entry_id={eid} fixed",
        context=SESSION,
    )


if __name__ == "__main__":
    main()
