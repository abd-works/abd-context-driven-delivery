"""failed_generate_log — shows Repair logging a generate step that produced wrong output."""
from __future__ import annotations

from repair.repair import Repair
from workspace.workspace_session import Session


class FailedGenerateLog:
    """Example: log a failed generate step to the session mistakes.log,
    then complete it once the fix lands."""

    def log_it(self, session_path: str) -> str:
        """Record that a generate step produced the wrong output under *session_path*.

        Instantiates Repair rooted at the session, calls log_mistake the
        moment the wrong output is spotted (before the fix exists), then
        calls log_correction once the fix is known - completing the same
        entry via its entry_id rather than opening a new one. Both calls
        together are appended to
        {session_path}/.context/sessions/{name}/mistakes.log.
        """
        repair = Repair(workspace=Session(path=session_path))
        entry_id = repair.log_mistake(
            artifact="output/story-map.md",
            rule="one-slice-per-tick",
            wrong="generate wrote the entire story map in a single tick instead of one unlocked slice",
            original="## Epic 1\n...\n## Epic 2\n...\n## Epic 3\n...",
        )
        return repair.log_correction(
            entry_id=entry_id,
            improved="## Epic 1\n  - Story 1.1 — as a customer I can browse products",
            status="fixed",
        )
