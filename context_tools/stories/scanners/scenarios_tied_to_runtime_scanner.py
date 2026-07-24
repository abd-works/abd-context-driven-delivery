"""scenarios-tied-to-runtime — boundary-crossing steps use concrete shapes."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_VAGUE_BOUNDARY = re.compile(
    r"\bthe\s+(service|api|backend|server|system)\b\s+(accepts|processes|handles|receives|takes)",
    re.IGNORECASE,
)


class ScenariosTiedToRuntimeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            for clause in sc.when_clauses + sc.then_clauses:
                if _VAGUE_BOUNDARY.search(clause.text):
                    yield self.violation(
                        f"Scenario {sc.name!r}: clause {clause.text!r} names a service "
                        f"boundary vaguely — use the concrete endpoint / event / "
                        f"queue / table",
                        location=self.loc(clause, f"scenario {sc.name!r}"),
                        severity="warning",
                    )
                    return
