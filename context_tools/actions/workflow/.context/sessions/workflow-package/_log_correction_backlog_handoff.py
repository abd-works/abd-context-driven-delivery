"""Correction turn — connected backlog handoff chain (sketch good through issue body)."""
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
            "Connected causal usage story: standing handoff context, backlog runs "
            "Handoff, created handoff outcomes, create issue with handoff in body, "
            "nested start under issue from backlog step, finish under open session. "
            "Removed workflow kit subject."
        ),
        prompt="log correction — backlog handoff connected usage story",
    )
    print(f"entry_id={ENTRY_ID}")
    print(f"turn_commit={sha or '(no commit)'}")


if __name__ == "__main__":
    main()
