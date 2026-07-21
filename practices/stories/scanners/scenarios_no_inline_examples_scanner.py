"""scenarios-no-inline-examples — concrete values belong in the Examples table."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner

_ITALIC_VALUE = re.compile(
    r"\*("
    r"[A-Z]{2,}-\d+"
    r"|\$[\d,]+(?:\.\d{2})?"
    r"|\d{1,2}:\d{2}\s*[A-Z]+"
    r"|\d[\d,.]*"
    r")\*"
)

_QUOTED_VALUE = re.compile(
    r'["\']([A-Z]{2,}-\d+|[A-Z][A-Z0-9_-]{2,}|\$[\d,]+(?:\.\d{2})?)["\']'
)


def _step_has_inline_example(text: str) -> bool:
    return bool(_ITALIC_VALUE.search(text) or _QUOTED_VALUE.search(text))


class ScenariosNoInlineExamplesScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            if sc.is_outline:
                continue
            offending = [
                clause for clause in sc.all_clauses
                if _step_has_inline_example(clause.text)
            ]
            if not offending:
                continue
            example_clause = offending[0]
            yield self.violation(
                f"Scenario {sc.name!r}: step {example_clause.text!r} contains "
                f"a concrete example value — use a Scenario Outline with "
                f"{{variable}} placeholders and move values to the Examples table",
                location=self.loc(sc, f"scenario {sc.name!r}"),
                severity="warning",
            )
