"""Correction turn — trim workspace scope from workflow sketch."""
from __future__ import annotations

from pathlib import Path

from _workspace_turn import log_correction_turn

SESSION = "workflow-package"
PATH = "context_tools/actions/workflow"
SKETCH = Path("context_tools/actions/workflow/.context/workflow-bdd-sketch.md")
ENTRY_ID = "7c6b38b2"


def main() -> None:
    improved = SKETCH.read_text(encoding="utf-8")
    sha = log_correction_turn(
        path=PATH,
        session_name=SESSION,
        entry_id=ENTRY_ID,
        improved=improved,
        how=(
            "Removed workspace git branch/dirty-tree/merge-conflict branches from "
            "start and finish. After open work session: it should set the branch to "
            "the session branch for that work session. Finish keeps workflow outcomes "
            "only (merge orchestration, Project Done, close issue, trailers)."
        ),
        prompt="log correction — workflow sketch workspace scope trimmed",
    )
    print(f"entry_id={ENTRY_ID}")
    print(f"turn_commit={sha or '(no commit)'}")


if __name__ == "__main__":
    main()
