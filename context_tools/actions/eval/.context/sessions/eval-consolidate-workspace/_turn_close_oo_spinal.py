"""Commit already-updated OO sketch — same git-primary spinal, wrongly left out of BDD turn."""
from context_tools.bdd.bdd import Bdd

bdd = Bdd(
    fidelity="behavior",
    path="context_tools/actions/eval",
    session="eval-consolidate-workspace",
)
bdd.open(
    name="eval-consolidate-workspace",
    goal="land OO sketch git-primary updates left out of BDD spinal turn",
    fidelities="behavior",
    path="context_tools/actions/eval",
)
bdd.begin_eval_turn()
print(
    bdd.finish_eval_turn(
        prompt="OO sketch — git-primary mistake/correction (same spinal as BDD)",
        result=(
            "workspace-eval-oo-sketch.md: Mistake.annotate / Correction.link; "
            "git notes + Fixes-Mistake trailers; session.yaml not association store; "
            "was updated with BDD spinal but stashed out of turn 1b68a70b — landed now"
        ),
        context="eval-consolidate-workspace",
    )
)
