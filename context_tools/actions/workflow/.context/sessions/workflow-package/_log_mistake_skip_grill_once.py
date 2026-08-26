"""Log mistake: skipped grill/AskQuestion before locking workflow sketch decisions."""
from __future__ import annotations

from pathlib import Path

from eval.session import EvalSession, Repair, repos_for_workspace
from workspace.workspace import Workspace

SESSION = "workflow-package"
PATH = "context_tools/actions/workflow"
SKETCH = Path(
    "context_tools/actions/workflow/.context/workflow-bdd-sketch.md"
)
INTRODUCING_SHA = "10fbeddb53522faf2a54011e982f96cb91ced34e"


def main() -> None:
    ws = Workspace(PATH)
    work_session = ws.open_work_session(name=SESSION, path=PATH)
    git, cdd_repo = repos_for_workspace(work_session)
    eval_session = EvalSession(workspace=work_session, git=git, cdd_repo=cdd_repo)
    repairer = Repair(session=eval_session)

    original = SKETCH.read_text(encoding="utf-8")
    entry_id = repairer.log_mistake(
        artifact=str(SKETCH).replace("\\", "/"),
        rule="(process) bdd-grill-sketch-workflow",
        wrong=(
            "Locked four grill ticks and committed sketch/scaffold without AskQuestion "
            "or grill turns; inferred v1 decisions and proceeded when user said proceed "
            "instead of logging mistake immediately when called out."
        ),
        original=original,
        tool="bdd",
        fidelity="behavior",
    )

    # Git-primary: note on introducing SHA (scaffold commit), not discovery turn.
    mistake = eval_session._find_mistake(entry_id)
    if mistake is not None:
        mistake._introducing_commit = INTRODUCING_SHA
        mistake.annotate(git)

    turn = eval_session.finish_turn(
        prompt="log mistake — skipped grill before locking workflow v1 decisions",
        result=f"entry_id={entry_id} introducing={INTRODUCING_SHA}",
        context=SESSION,
    )
    sha = turn.change_commit.sha if turn and turn.change_commit else "(no commit — clean tree)"
    print(f"entry_id={entry_id}")
    print(f"turn_commit={sha}")


if __name__ == "__main__":
    main()
