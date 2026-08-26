"""Log correction for mistake 62fc32d6 — grill-complete sketch + aligned scaffold."""
from __future__ import annotations

from pathlib import Path

from _workspace_turn import log_correction_turn

SESSION = "workflow-package"
PATH = "context_tools/actions/workflow"
SKETCH = Path("context_tools/actions/workflow/.context/workflow-bdd-sketch.md")
ENTRY_ID = "62fc32d6"


def main() -> None:
    improved = SKETCH.read_text(encoding="utf-8")
    sha = log_correction_turn(
        path=PATH,
        session_name=SESSION,
        entry_id=ENTRY_ID,
        improved=improved,
        how=(
            "Grill-complete v1 locked; reshaped sketch to usage-story taxonomy "
            "(subject → action run → standing with → enabling that → business-state "
            "it should); issue body canonical handoff; GitHub # only; Project "
            "Backlog/In Progress/Done; aligned module-context and workflow.py "
            "(removed CDD-N/tickets.jsonl/backlog folder tools)."
        ),
        prompt="log correction — workflow sketch grill-complete usage story",
    )
    print(f"entry_id={ENTRY_ID}")
    print(f"turn_commit={sha or '(no commit — clean tree)'}")


if __name__ == "__main__":
    main()
