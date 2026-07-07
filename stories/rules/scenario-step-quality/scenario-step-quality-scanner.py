"""scenario-step-quality — keyword roles are used correctly.

Mechanical checks on `workspace.scenarios`:
- Two consecutive When steps (with no Then between them) is a smell — the
  second When is a system reaction that should be an And.
- A Then/And/But clause containing "when ... is true/false" embeds inline
  conditional logic inside an assertion — a Scenario Outline anti-pattern.
  Each row in the Examples table is a complete, independent test; conditions
  belong in the row data, not as guards inside step text.

Domain-language readability and Given placement are AI-judge territory —
this scanner catches only coarse structural failures.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402

# Matches patterns like "when {memo_saved} is true" or "when <var> is false"
# embedded inside a Then/And/But assertion step.
_INLINE_CONDITIONAL = re.compile(
    r"\bwhen\s+[<{]?\w+[>}]?\s+is\s+(?:true|false)\b", re.IGNORECASE
)


class ScenarioStepQualityScanner(ArtifactScanner):
    """Every when-block must be followed by an observed then-block, and
    Then steps must not embed inline conditional guards."""
    rule = "scenario-step-quality"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            # Check 1: back-to-back When blocks (missing Then observation).
            for interaction in sc.interactions[:-1]:
                if not interaction.then and interaction.when:
                    first_when = interaction.when[0]
                    yield Violation(
                        rule=self.rule,
                        message=(
                            f"Scenario {sc.name!r} has a when-block with no observed "
                            f"then before a new When begins — chain follow-on triggers "
                            f"with And, not a bare When"
                        ),
                        location=self.location(
                            first_when.source, f"scenario {sc.name!r}"
                        ),
                        severity="warning",
                        hint=(
                            "One distinct trigger per When. Continue system reactions "
                            "inside the same when-block using `*And*` continuations."
                        ),
                    )
                    return

            # Check 2: inline "when {var} is true/false" guards in Then steps.
            for interaction in sc.interactions:
                for clause in interaction.then:
                    if _INLINE_CONDITIONAL.search(clause.text):
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario {sc.name!r} has a Then step with an inline "
                                f"conditional guard ('when ... is true/false'): "
                                f"{clause.text!r}"
                            ),
                            location=self.location(
                                clause.source, f"scenario {sc.name!r}"
                            ),
                            severity="error",
                            hint=(
                                "Each Scenario Outline row is a complete independent "
                                "execution — split positive and negative outcomes into "
                                "separate outlines rather than embedding conditions "
                                "inside Then steps."
                            ),
                        )


if __name__ == "__main__":
    sys.exit(run(ScenarioStepQualityScanner))
