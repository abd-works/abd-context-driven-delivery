"""scenario-step-quality - keyword roles are used correctly."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_INLINE_CONDITIONAL = re.compile(
    r"\bwhen\s+[<{]?\w+[>}]?\s+is\s+(?:true|false)\b", re.IGNORECASE
)


class ScenarioStepQualityScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            for interaction in sc.interactions[:-1]:
                if not interaction.then and interaction.when:
                    first_when = interaction.when[0]
                    yield self.violation(
                        f"Scenario {sc.name!r} has a when-block with no observed "
                        f"then before a new When begins - chain follow-on triggers "
                        f"with And, not a bare When",
                        location=self.loc(first_when, f"scenario {sc.name!r}"),
                        severity="warning",
                    )
                    return

            for interaction in sc.interactions:
                for clause in interaction.then:
                    if _INLINE_CONDITIONAL.search(clause.text):
                        yield self.violation(
                            f"Scenario {sc.name!r} has a Then step with an inline "
                            f"conditional guard ('when ... is true/false'): "
                            f"{clause.text!r}",
                            location=self.loc(clause, f"scenario {sc.name!r}"),
                            severity="error",
                        )
