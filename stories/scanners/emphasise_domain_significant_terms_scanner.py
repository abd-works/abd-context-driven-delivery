"""emphasise-domain-significant-terms — scenario steps use bold/italic emphasis."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class EmphasiseDomainSignificantTermsScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            clauses = sc.all_clauses
            if not clauses:
                continue
            has_emphasis = any(
                bool(clause.concepts) or bool(clause.values) for clause in clauses
            )
            if not has_emphasis:
                yield self.violation(
                    f"Scenario {sc.name!r} has no bold concepts or italic values "
                    f"in any step — domain-significant terms should be emphasised",
                    location=self.loc(sc, f"scenario {sc.name!r}"),
                    severity="warning",
                )
