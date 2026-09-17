"""factory-backed-examples - placeholders must resolve via factory or example rows.

Preferred: concrete values live in {Type}ExampleFactory. Legacy outline
example_rows are still checked for column/placeholder alignment when present.
"""

from __future__ import annotations

import re
from typing import Set

from story_workspace_base import StoryWorkspaceScanner

_PLACEHOLDER = re.compile(r"[<{]([a-zA-Z_][a-zA-Z0-9_]*)[>}]")


class ScenarioOutlineStructureScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            if not sc.is_outline:
                continue

            placeholders: Set[str] = set()
            for clause in sc.all_clauses:
                placeholders.update(_PLACEHOLDER.findall(clause.text))

            # Factory-backed stories: no inventable example table required.
            if not sc.example_rows:
                if placeholders:
                    yield self.violation(
                        f"Scenario {sc.name!r} uses placeholders "
                        f"{sorted(placeholders)} - resolve them via "
                        f"examples/ or givens.ts (not inline values in the story)",
                        location=self.loc(sc, f"scenario {sc.name!r}"),
                        severity="warning",
                    )
                continue

            headers: Set[str] = set()
            for row in sc.example_rows:
                headers.update(row.keys())

            missing_columns = placeholders - headers
            if missing_columns:
                yield self.violation(
                    f"Scenario Outline {sc.name!r} uses placeholders "
                    f"{sorted(missing_columns)} that have no matching example-table column "
                    f"(prefer factory examples over story-local tables)",
                    location=self.loc(sc, f"scenario outline {sc.name!r}"),
                    severity="error",
                )
