"""One process: log validate mistake + correction on workflow-package session."""
from __future__ import annotations

from context_tools.clean_engineering.clean_engineering import CleanEngineering

SESSION = "workflow-package"
PATH = "utilities/git"


def main() -> None:
    ce = CleanEngineering(fidelity="modules", path=PATH, session=SESSION, workspace=".")
    ce.workspace.open(ce)
    git = ce.workspace.current_work_session.git
    introducing = git.current_commit if hasattr(git, "current_commit") else ""

    ce.begin_turn(action="mistake")
    eid = ce.record_mistake(
        artifact=PATH,
        rule="validate-do-not-edit",
        wrong=(
            "User invoked validate + scan on utilities/git but the agent edited during validate "
            "— wrote module-context.md/git-modules.md, privatized _cli.py, fixed output-format — "
            "instead of critical-judge report-only (scan + pass/fail evidence, no fixes)."
        ),
        original=(
            "base_context_tool.md # Validate: (1) session_guidance scope "
            "(2) contexts rubric pass/fail (3) call scan (4) Do not fix."
        ),
        introducing_commit=introducing,
        tool="clean_engineering",
        fidelity="modules",
    )
    ce.finish_turn(
        prompt="log mistake — edited during validate instead of report-only",
        result=f"entry_id={eid}",
        context=SESSION,
    )

    ce.begin_turn(action="correction")
    ce.record_correction(
        entry_id=eid,
        improved="",
        how=(
            "On validate: run tools.ps1 validate + scan only; report pass/fail per named rule "
            "with evidence; defer edits to satisfy. deep-module _cli fix belongs in satisfy, "
            "not validate."
        ),
        status="fixed",
    )
    ce.finish_turn(
        prompt="log correction — validate is report-only; satisfy owns fixes",
        result=f"entry_id={eid} fixed",
        context=SESSION,
    )
    print(eid)


if __name__ == "__main__":
    main()
