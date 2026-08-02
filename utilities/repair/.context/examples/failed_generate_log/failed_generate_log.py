"""failed_generate_log — shows Repair logging a generate step that produced wrong output."""
from __future__ import annotations

from repair.repair import Repair


class FailedGenerateLog:
    """Example: log a failed generate step to the session to-fix.log."""

    def log_it(self, session_path: str) -> str:
        """Record that a generate step produced the wrong output under *session_path*.

        Instantiates Repair rooted at the session, then calls write_to_fix so
        the failure is appended to {session_path}/.context/sessions/{name}/to-fix.log
        with the artifact, the violated rule, and the corrected output.
        """
        repair = Repair(path=session_path)
        return repair.write_to_fix(
            artifact="output/story-map.md",
            rule="one-slice-per-tick",
            wrong="generate wrote the entire story map in a single tick instead of one unlocked slice",
            original="## Epic 1\n...\n## Epic 2\n...\n## Epic 3\n...",
            improved="## Epic 1\n  - Story 1.1 — as a customer I can browse products",
            status="fixed",
        )
