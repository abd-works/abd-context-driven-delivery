"""real-data-over-invented-values - no placeholder values in scenarios."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner

_PLACEHOLDERS = {
    "foo", "bar", "baz", "qux", "test", "example", "sample", "placeholder",
    "user1", "user2", "user123", "1", "1.00", "123", "abc", "xyz",
}


def _is_placeholder(value: str) -> bool:
    stripped = value.strip().strip("`*").lower()
    return stripped in _PLACEHOLDERS


class RealDataOverInventedValuesScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for sc in workspace.scenarios:
            for clause in sc.all_clauses:
                for value in clause.values:
                    if _is_placeholder(value):
                        yield self.violation(
                            f"Scenario {sc.name!r} uses placeholder value "
                            f"{value!r} in a {clause.phase.value} clause",
                            location=self.loc(clause, f"scenario {sc.name!r}"),
                            severity="warning",
                        )
                        return
            for row in sc.example_rows:
                for header, cell in row.items():
                    if _is_placeholder(cell):
                        yield self.violation(
                            f"Scenario Outline {sc.name!r} has placeholder "
                            f"value {cell!r} in column {header!r}",
                            location=self.loc(sc, f"scenario outline {sc.name!r}"),
                            severity="warning",
                        )
                        return
