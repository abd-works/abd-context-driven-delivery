"""scenario-outline-structure — outlines have example rows and matching placeholders.

Mechanical checks on `workspace.scenarios`:
- Every Scenario with `is_outline=True` has at least one row in `example_rows`.
- Every `<placeholder>` in the outline's step text corresponds to a header in
  the example rows.

Choosing "key examples" versus enumeration is AI-judge territory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


# Both <placeholder> and {placeholder} are accepted outline variable syntaxes.
_PLACEHOLDER = re.compile(r"[<{]([a-zA-Z_][a-zA-Z0-9_]*)[>}]")


class ScenarioOutlineStructureScanner(ArtifactScanner):
    """Scenario outlines have example rows and matching placeholders."""
    rule = "scenario-outline-structure"
    kind = "shape"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            if not sc.is_outline:
                continue
            if not sc.example_rows:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Scenario Outline {sc.name!r} has no example rows"
                    ),
                    location=self.location(sc.source, f"scenario outline {sc.name!r}"),
                    severity="error",
                    hint="Add an `### Examples` block with a table of key examples",
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
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Scenario Outline {sc.name!r} uses placeholders "
                        f"{sorted(missing_columns)} that have no matching example-table column"
                    ),
                    location=self.location(sc.source, f"scenario outline {sc.name!r}"),
                    severity="error",
                    hint="Every `<placeholder>` in the outline must appear as a column header",
                )


if __name__ == "__main__":
    sys.exit(run(ScenarioOutlineStructureScanner))
