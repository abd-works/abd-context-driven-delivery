"""Mistake turn only — wrong grill question style in grill-answers tick 9."""
from __future__ import annotations

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
ARTIFACT = (
    "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md"
)
ORIGINAL = """### Turn — grill tick 9 — slice F boundary (mistake / correction)

**Question:** Slice **F** extends the workspace Bdd sketch for the mistake/correction chain (`workspace-eval-oo-sketch.md` §4 lines 264, 393–394, 427–446, 660–683; §9 item 6). Where should the **first** sketch extension boundary fall?

**Options:**

- **A — Mistake-only under open turn:** enabling event when recording a mistake → on open turn, persist under work session, nest in themed repair backlog. Exclude correction and TurnCommit.mistakeIds until later tick.
- **B — Mistake + correction same open turn:** both sibling enabling events under `that has a turn open` in one action run, before finish_turn.
- **C — Separate action runs:** mistake under one action run's open turn; correction under a **later** action run's open turn. TurnCommit mistakeIds only when mistakes recorded on that turn.
- **D — Workspace sketch stops at turn envelope:** Mistake/Correction/Repair in eval-module Bdd sketch only; keep workspace deferred.

**Answer (user):** **B — Mistake + correction same open turn** — sibling enabling events under `that has a turn open` in one action run.
"""


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()
    bdd.begin_eval_turn()
    eid = bdd.log_mistake(
        artifact=ARTIFACT,
        rule="usage-order-behaviors",
        wrong=(
            "Grill tick 9 asked slice-boundary / process options (where should the first "
            "extension boundary fall) instead of BDD design-tree questions: highest-level "
            "behavior, event, or state change to model; substates under that branch; "
            "legitimate it should tests. bdd.md: nest by enabling events and usage story — "
            "grill must walk the tree down, not pick sketch scope by checklist letter."
        ),
        original=ORIGINAL,
    )
    bdd.finish_eval_turn(
        prompt="log mistake — wrong grill question style tick 9",
        result=f"entry_id={eid}",
        context=SESSION,
    )
    print(eid)


if __name__ == "__main__":
    main()
