"""alternate-actor-emphasis — no 3+ consecutive same-actor beats in a scenario."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_USER_TOKENS = (
    "user", "actor", "customer", "developer", "human", "cli", "repl",
    "merchant", "agent", "treasurer", "approver", "auditor", "operator",
)
_SYSTEM_TOKENS = (
    "system", "bot", "application", "server", "workflow", "service", "api",
    "backend", "frontend", "database", "gateway",
)


def _classify(text: str) -> str:
    low = text.lower()
    for tok in _USER_TOKENS:
        if re.search(rf"\b{tok}\b", low):
            return "user"
    for tok in _SYSTEM_TOKENS:
        if re.search(rf"\b{tok}\b", low):
            return "system"
    return "system"


class AlternateActorEmphasisScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            clauses = sc.all_clauses
            if len(clauses) < 3:
                continue
            run_len = 1
            prev_kind = _classify(clauses[0].text)
            for step in clauses[1:]:
                kind = _classify(step.text)
                if kind == prev_kind:
                    run_len += 1
                    if run_len >= 3:
                        yield self.violation(
                            f"Scenario {sc.name!r} has {run_len} consecutive "
                            f"{prev_kind}-only steps — insert the missing beat "
                            f"from the other actor or split the story",
                            location=self.loc(sc, f"scenario {sc.name!r}"),
                            severity="warning",
                        )
                        break
                else:
                    run_len = 1
                    prev_kind = kind
