"""scenario-outline-structure — outlines have example rows and matching placeholders."""

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
            if not sc.example_rows:
                yield self.violation(
                    f"Scenario Outline {sc.name!r} has no example rows",
                    location=self.loc(sc, f"scenario outline {sc.name!r}"),
                    severity="error",
                )
                continue

            headers: Set[str] = set()
            for row in sc.example_rows:
                headers.update(row.keys())

            placeholders: Set[str] = set()
            for clause in sc.all_clauses:
                placeholders.update(_PLACEHOLDER.findall(clause.text))

            missing_columns = placeholders - headers
            if missing_columns:
                yield self.violation(
                    f"Scenario Outline {sc.name!r} uses placeholders "
                    f"{sorted(missing_columns)} that have no matching example-table column",
                    location=self.loc(sc, f"scenario outline {sc.name!r}"),
                    severity="error",
                )
