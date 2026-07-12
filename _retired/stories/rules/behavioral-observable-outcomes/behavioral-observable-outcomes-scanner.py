"""behavioral-observable-outcomes — Then/And/But steps describe observable outcomes.

Mechanical check on `workspace.scenarios`:
- Then, And, and But step text must not use internal-mechanic verbs.

Banned verbs from the rule doc: `records`, `triggers`, `sets`, `loads`,
`accepts` (as internal state), `processes`, `handles`, `manages`.

Full observability semantics are AI-judge territory; this scanner catches
the common internal-mechanic verb smell.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_INTERNAL_VERBS = ("records", "triggers", "sets", "loads", "processes", "handles", "manages")


class BehavioralObservableOutcomesScanner(ArtifactScanner):
    """Then-clauses avoid internal-mechanic verbs.

    Walks every clause in every interaction's `then` list (that includes the
    lead Then plus any `And` / `But` continuations riding after it).
    """
    rule = "behavioral-observable-outcomes"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            for clause in sc.then_clauses:
                for verb in _INTERNAL_VERBS:
                    if re.search(rf"\b{verb}\b", clause.text.lower()):
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario {sc.name!r}: then-clause uses internal-"
                                f"mechanic verb {verb!r} — describe the observable "
                                f"outcome instead"
                            ),
                            location=self.location(clause.source, f"scenario {sc.name!r}"),
                            severity="warning",
                            hint=(
                                "State what is shown / displayed / marked as / "
                                "created / received in domain terms"
                            ),
                        )
                        return


if __name__ == "__main__":
    sys.exit(run(BehavioralObservableOutcomesScanner))
