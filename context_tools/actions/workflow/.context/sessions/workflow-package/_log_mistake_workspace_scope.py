"""Mistake turn — workflow sketch duplicated workspace git/session branch scope."""
from __future__ import annotations

from eval.session import EvalSession, Repair, repos_for_workspace
from workspace.workspace import Workspace

SESSION = "workflow-package"
PATH = "context_tools/actions/workflow"
ARTIFACT = "context_tools/actions/workflow/.context/workflow-bdd-sketch.md"

ORIGINAL_EXCERPT = """\
          it should set the current work session to that work session
          with HEAD already on its session branch
            it should continue without switching branch
          with a clean working tree not on its session branch
            with an existing session branch for that ticket
              it should check out that session branch
            with no session branch yet
              it should create the session branch for that work session
          with a dirty working tree not on its session branch
            it should refuse to switch branch
...
              with a clean mergeable session branch
              with a dirty working tree
                it should refuse to merge until the tree is clean
              with merge conflicts
                it should report the conflict and leave the session open
"""


def main() -> None:
    ws = Workspace(PATH)
    work_session = ws.open_work_session(name=SESSION, path=PATH)
    git, cdd_repo = repos_for_workspace(work_session)
    eval_session = EvalSession(workspace=work_session, git=git, cdd_repo=cdd_repo)
    repairer = Repair(session=eval_session)

    entry_id = repairer.log_mistake(
        artifact=ARTIFACT,
        rule="layer-isolation",
        wrong=(
            "Copied workspace git branch policy into workflow sketch — HEAD on session "
            "branch, clean/dirty tree checkout/create/refuse, mergeable branch, merge "
            "conflicts. Workflow depends on workspace for that; its scope is validate "
            "session opened and branch set for the work session after start, plus "
            "workflow outcomes (Project status, issue body, trailers, finish orchestration)."
        ),
        original=ORIGINAL_EXCERPT,
        tool="bdd",
        fidelity="behavior",
    )

    turn = eval_session.finish_turn(
        prompt="log mistake — workflow sketch duplicated workspace scope",
        result=f"entry_id={entry_id}",
        context=SESSION,
    )
    sha = turn.change_commit.sha if turn and turn.change_commit else "(no commit)"
    print(f"entry_id={entry_id}")
    print(f"turn_commit={sha}")


if __name__ == "__main__":
    main()
