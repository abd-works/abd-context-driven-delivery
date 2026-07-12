"""real-data-over-invented-values — no placeholder values in scenarios or outline tables.

Mechanical check on `workspace.scenarios`:
- Every value (italic value in a step, or cell in an example row) must not
  be in the banned placeholder set: foo, bar, baz, qux, test, example,
  User1, User2, John, Jane, 1.00, 123, abc, xyz.

Realistic domain values (`10000.00 USD`, `USR-001`, `Jane Doe`) pass.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_PLACEHOLDERS = {
    "foo", "bar", "baz", "qux", "test", "example", "sample", "placeholder",
    "user1", "user2", "user123", "1", "1.00", "123", "abc", "xyz",
}


def _is_placeholder(value: str) -> bool:
    stripped = value.strip().strip("`*").lower()
    return stripped in _PLACEHOLDERS


class RealDataOverInventedValuesScanner(ArtifactScanner):
    """No placeholder values in scenario steps or example rows."""
    rule = "real-data-over-invented-values"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            for clause in sc.all_clauses:
                for value in clause.values:
                    if _is_placeholder(value):
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario {sc.name!r} uses placeholder value "
                                f"{value!r} in a {clause.phase.value} clause"
                            ),
                            location=self.location(clause.source, f"scenario {sc.name!r}"),
                            severity="warning",
                            hint=(
                                "Use realistic domain values (e.g. `10000.00 USD`, "
                                "`Jane Doe`, `USR-001`) drawn from source material"
                            ),
                        )
                        return
            for row in sc.example_rows:
                for header, cell in row.items():
                    if _is_placeholder(cell):
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario Outline {sc.name!r} has placeholder "
                                f"value {cell!r} in column {header!r}"
                            ),
                            location=self.location(sc.source, f"scenario outline {sc.name!r}"),
                            severity="warning",
                        )
                        return


if __name__ == "__main__":
    sys.exit(run(RealDataOverInventedValuesScanner))
