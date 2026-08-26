"""Log mistake: skipped grill/AskQuestion before locking workflow sketch decisions."""
from __future__ import annotations

from pathlib import Path

from _workspace_turn import log_mistake_turn

SESSION = "workflow-package"
PATH = "context_tools/actions/workflow"
SKETCH = Path(
    "context_tools/actions/workflow/.context/workflow-bdd-sketch.md"
)
INTRODUCING_SHA = "10fbeddb53522faf2a54011e982f96cb91ced34e"


def main() -> None:
    original = SKETCH.read_text(encoding="utf-8")
    entry_id, sha = log_mistake_turn(
        path=PATH,
        session_name=SESSION,
        artifact=str(SKETCH).replace("\\", "/"),
        rule="(process) bdd-grill-sketch-workflow",
        wrong=(
            "Locked four grill ticks and committed sketch/scaffold without AskQuestion "
            "or grill turns; inferred v1 decisions and proceeded when user said proceed "
            "instead of logging mistake immediately when called out."
        ),
        original=original,
        introducing_commit=INTRODUCING_SHA,
        prompt="log mistake — skipped grill before locking workflow v1 decisions",
    )
    print(f"entry_id={entry_id}")
    print(f"turn_commit={sha or '(no commit — clean tree)'}")


if __name__ == "__main__":
    main()
