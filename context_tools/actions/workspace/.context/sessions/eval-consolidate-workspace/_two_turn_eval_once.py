"""Two-turn eval: mistake turn then correction turn — one process each."""
from __future__ import annotations

from pathlib import Path

from context_tools.bdd.bdd import Bdd

SESSION = "eval-consolidate-workspace"
PATH = "context_tools/actions/workspace"
WORKFLOW = Path("context_tools/bdd/.context/bdd-grill-sketch-workflow.md")
WRONG_SNIPPET = (
    "bdd.begin_eval_turn()\n"
    "entry_id = bdd.log_mistake(...)\n"
    "bdd.log_correction(entry_id=entry_id, ...)\n"
    "bdd.finish_eval_turn(...)\n"
)


def main() -> None:
    bdd = Bdd(fidelity="behavior", path=PATH, session=SESSION)
    bdd.open()

    bdd.begin_eval_turn()
    entry_id = bdd.log_mistake(
        artifact=str(WORKFLOW).replace("\\", "/"),
        rule="eval-turn-single-process",
        wrong=(
            "Documented log_mistake and log_correction in the same turn / same finish_eval_turn. "
            "Mistake and correction are separate turns; only begin+tool+finish share one process per turn."
        ),
        original=WRONG_SNIPPET,
    )
    mid = bdd.finish_eval_turn(
        prompt="log mistake — same-turn mistake+correction doc error",
        result=f"entry_id={entry_id}",
        context=SESSION,
    )
    print(f"mistake turn {mid} entry_id={entry_id}")

    bdd.begin_eval_turn()
    bdd.log_correction(
        entry_id=entry_id,
        improved=WORKFLOW.read_text(encoding="utf-8"),
        how="bdd-grill-sketch-workflow.md: two turns; one process per turn; not same turn for mistake+correction.",
        status="fixed",
    )
    end = bdd.finish_eval_turn(
        prompt="log correction — two-turn eval model",
        result=f"entry_id={entry_id} fixed; workflow + improvement.md updated",
        context=SESSION,
    )
    print(f"correction turn {end}")


if __name__ == "__main__":
    main()
