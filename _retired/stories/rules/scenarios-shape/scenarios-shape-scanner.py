"""scenarios-shape — validates the fundamental Gherkin skeleton.

Required members:
1. At least one Scenario loaded from workspace.scenarios
2. Every Scenario has at least one Given, at least one When, at least one Then
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class ScenariosShapeScanner(ArtifactScanner):
    """Every scenario has given, at least one interaction with when + then.

    In the phase-grouped model, a well-formed scenario has:
      - `given` non-empty
      - at least one `interaction` with `when` and `then` both non-empty
    """
    rule = "scenarios-shape"
    kind = "shape"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_scenarios():
            yield Violation(
                rule=self.rule,
                message="No scenarios found",
                location="scenarios/",
                severity="error",
                hint="Add at least one `### Scenario N: <name>` block under `scenarios/*.md`",
            )
            return

        for scenario in self.workspace.scenarios:
            missing: list[str] = []
            if not scenario.given:
                missing.append("Given")
            has_full_interaction = any(i.when and i.then for i in scenario.interactions)
            if not has_full_interaction:
                if not scenario.when_clauses:
                    missing.append("When")
                if not scenario.then_clauses:
                    missing.append("Then")
            if missing:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Scenario {scenario.name!r} is missing required phase(s): "
                        f"{', '.join(missing)}"
                    ),
                    location=self.location(
                        getattr(scenario, "source", None),
                        f"scenario {scenario.name!r}",
                    ),
                    severity="error",
                    hint=(
                        "Every scenario needs at least one *Given*, one *When*, and one *Then* step"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(ScenariosShapeScanner))
