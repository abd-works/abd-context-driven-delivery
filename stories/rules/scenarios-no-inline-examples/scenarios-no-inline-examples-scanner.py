"""scenarios-no-inline-examples — concrete example values must live in the Examples table.

A non-outline Scenario whose step text contains patterns that look like concrete
example data (quoted IDs, currency amounts, italic-wrapped values, specific
identifiers) should be a Scenario Outline with {variable} placeholders instead.

Concrete values in step text are a smell that specification-level data has
leaked into the scenario structure. The correct form moves those values into
the `### Examples` table and replaces them with `{variable}` placeholders so
the scenario describes the behavior, not a single data point.

Failure smells:
- Step text with italic-wrapped IDs: `*CHK-001*`, `*T-001*`, `*ACH-999*`
- Step text with dollar amounts: `*$50,000.00*`, `$250,000.00`
- Step text with time literals: `*15:00 ET*`
- Step text with quoted concrete values: `"CHK-001"`, `"DRAFT"`

The inline format (`scenario-inline.md`) is opt-in and must be explicitly
requested. Scenario Outline is the default.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path  # noqa: F401 — kept for workspace.root access
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402

# Patterns that indicate concrete example values embedded in step text.

# Italic-wrapped token that looks like a data value (not a role/concept name):
#   *CHK-001*, *T-001*, *ACH-999*, *$50,000.00*, *15:00 ET*, *Draft*, *Valid*
# Heuristic: italic token that contains a digit, special char, or looks like an
# identifier (all-caps with hyphens/digits, or a dollar/time pattern).
_ITALIC_VALUE = re.compile(
    r"\*("
    r"[A-Z]{2,}-\d+"          # ID: CHK-001, T-001, ACH-999
    r"|\$[\d,]+(?:\.\d{2})?"  # currency: $50,000.00
    r"|\d{1,2}:\d{2}\s*[A-Z]+"  # time: 15:00 ET
    r"|\d[\d,.]*"              # bare number: 250000, 15
    r")\*"
)

# Quoted concrete value (double or single quotes around a non-placeholder token)
_QUOTED_VALUE = re.compile(
    r'["\']([A-Z]{2,}-\d+|[A-Z][A-Z0-9_-]{2,}|\$[\d,]+(?:\.\d{2})?)["\']'
)


def _step_has_inline_example(text: str) -> bool:
    return bool(_ITALIC_VALUE.search(text) or _QUOTED_VALUE.search(text))


class ScenariosNoInlineExamplesScanner(ArtifactScanner):
    """Non-outline scenarios must not embed concrete example values in step text."""

    rule = "scenarios-no-inline-examples"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            if sc.is_outline:
                continue

            offending_clauses = [
                clause for clause in sc.all_clauses
                if _step_has_inline_example(clause.text)
            ]
            if not offending_clauses:
                continue

            example_clause = offending_clauses[0]
            yield Violation(
                rule=self.rule,
                message=(
                    f"Scenario {sc.name!r}: step {example_clause.text!r} contains "
                    f"a concrete example value — use a Scenario Outline with "
                    f"{{variable}} placeholders and move values to the Examples table"
                ),
                location=self.location(sc.source, f"scenario {sc.name!r}"),
                severity="warning",
                hint=(
                    "Change `Scenario` to `Scenario Outline`, replace concrete "
                    "values with `{variable}` placeholders in every step, and add "
                    "a `### Examples` table with those values as columns. "
                    "Inline format is opt-in only."
                ),
            )


if __name__ == "__main__":
    sys.exit(run(ScenariosNoInlineExamplesScanner))
