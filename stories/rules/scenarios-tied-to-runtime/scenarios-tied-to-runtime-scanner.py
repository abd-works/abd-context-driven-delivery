"""scenarios-tied-to-runtime — steps that cross a boundary use concrete shapes.

Mechanical check: When steps that reference a service must use a concrete
runtime tie (HTTP method + path, event name, queue name, or table name).

Failure smells:
- `the service ...`, `the API ...`, `the backend ...` — generic, no concrete
  endpoint

Schema-tie and stub-tie enforcement are AI-judge territory (needs the actual
schema/stub files present); this scanner catches the vaguest failure mode.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_VAGUE_BOUNDARY = re.compile(
    r"\bthe\s+(service|api|backend|server|system)\b\s+(accepts|processes|handles|receives|takes)",
    re.IGNORECASE,
)


class ScenariosTiedToRuntimeScanner(ArtifactScanner):
    """Scenarios crossing boundaries use concrete endpoint/event names.

    Looks at the when-clauses and then-clauses of every scenario (the action
    and the observed outcome) — never at the given-clauses, which describe
    setup rather than boundary crossings.
    """
    rule = "scenarios-tied-to-runtime"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            for clause in sc.when_clauses + sc.then_clauses:
                if _VAGUE_BOUNDARY.search(clause.text):
                    yield Violation(
                        rule=self.rule,
                        message=(
                            f"Scenario {sc.name!r}: clause {clause.text!r} names a service "
                            f"boundary vaguely — use the concrete endpoint / event / "
                            f"queue / table"
                        ),
                        location=self.location(clause.source, f"scenario {sc.name!r}"),
                        severity="warning",
                        hint=(
                            "Replace 'the service accepts it' with the runtime shape: "
                            "'POSTs to /v2/payments' / 'emits event PaymentAccepted' / "
                            "'enqueues to payments-in'"
                        ),
                    )
                    return


if __name__ == "__main__":
    sys.exit(run(ScenariosTiedToRuntimeScanner))
