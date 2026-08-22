"""Close eval turn for BDD sketch spinal (git-primary mistake/correction)."""
from context_tools.bdd.bdd import Bdd

bdd = Bdd(
    fidelity="behavior",
    path="context_tools/actions/eval",
    session="eval-consolidate-workspace",
)
bdd.open(
    name="eval-consolidate-workspace",
    goal="close turn — BDD sketch spinal git-primary",
    fidelities="behavior",
    path="context_tools/actions/eval",
)
bdd.begin_eval_turn()
# Spinal already on disk: workspace-bdd-sketch.md (both copies) + LOCKED payloads
print(
    bdd.finish_eval_turn(
        prompt="BDD sketch spinal — git-primary mistake/correction",
        result=(
            "LOCKED association + payloads; mistake notes on introducing commit; "
            "correction commit trailers/payload; merge topology deferred; "
            "both session sketch copies synced"
        ),
        context="eval-consolidate-workspace",
    )
)
