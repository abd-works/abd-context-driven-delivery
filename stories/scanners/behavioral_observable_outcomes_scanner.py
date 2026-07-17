"""behavioral-observable-outcomes — Then steps describe observable outcomes."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_INTERNAL_VERBS = (
    "records", "triggers", "sets", "loads", "processes", "handles", "manages",
)


class BehavioralObservableOutcomesScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            for clause in sc.then_clauses:
                for verb in _INTERNAL_VERBS:
                    if re.search(rf"\b{verb}\b", clause.text.lower()):
                        yield self.violation(
                            f"Scenario {sc.name!r}: then-clause uses internal-"
                            f"mechanic verb {verb!r} — describe the observable "
                            f"outcome instead",
                            location=self.loc(clause, f"scenario {sc.name!r}"),
                            severity="warning",
                        )
                        return
