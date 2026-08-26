"""Correction turn — connected backlog handoff chain (sketch good through issue body)."""
from __future__ import annotations

from pathlib import Path

from eval.session import EvalSession, Repair, repos_for_workspace
from workspace.workspace import Workspace

SESSION = "workflow-package"
PATH = "context_tools/actions/workflow"
SKETCH = Path("context_tools/actions/workflow/.context/workflow-bdd-sketch.md")
ENTRY_ID = "62fc32d6"


def main() -> None:
    ws = Workspace(PATH)
    work_session = ws.open_work_session(name=SESSION, path=PATH)
    git, cdd_repo = repos_for_workspace(work_session)
    eval_session = EvalSession(workspace=work_session, git=git, cdd_repo=cdd_repo)
    repairer = Repair(session=eval_session)

    improved = SKETCH.read_text(encoding="utf-8")
    repairer.log_correction(
        entry_id=ENTRY_ID,
        improved=improved,
        how=(
            "Connected causal usage story: standing handoff context, backlog runs "
            "Handoff, created handoff outcomes, create issue with handoff in body, "
            "nested start under issue from backlog step, finish under open session. "
            "Removed workflow kit subject."
        ),
        status="fixed",
    )

    turn = eval_session.finish_turn(
        prompt="log correction — backlog handoff connected usage story",
        result=f"entry_id={ENTRY_ID} fixed",
        context=SESSION,
    )
    sha = turn.change_commit.sha if turn and turn.change_commit else "(no commit)"
    print(f"entry_id={ENTRY_ID}")
    print(f"turn_commit={sha}")


if __name__ == "__main__":
    main()
