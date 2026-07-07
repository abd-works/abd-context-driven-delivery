"""alternate-actor-emphasis — no 3+ consecutive same-actor beats in a scenario.

For each Scenario, classify each step body as user-visible or system-visible
via keyword heuristics. Three or more consecutive same-kind steps indicate a
missing beat or a story that should split.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_USER_TOKENS = ("user", "actor", "customer", "developer", "human", "cli", "repl",
                "merchant", "agent", "treasurer", "approver", "auditor", "operator")
_SYSTEM_TOKENS = ("system", "bot", "application", "server", "workflow", "service", "api",
                  "backend", "frontend", "database", "gateway")


def _classify(text: str) -> str:
    low = text.lower()
    for tok in _USER_TOKENS:
        if re.search(rf"\b{tok}\b", low):
            return "user"
    for tok in _SYSTEM_TOKENS:
        if re.search(rf"\b{tok}\b", low):
            return "system"
    return "system"


class AlternateActorEmphasisScanner(ArtifactScanner):
    """No 3+ consecutive same-actor beats in a scenario."""
    rule = "alternate-actor-emphasis"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            clauses = sc.all_clauses
            if len(clauses) < 3:
                continue
            run_len = 1
            prev_kind = _classify(clauses[0].text)
            for step in clauses[1:]:
                kind = _classify(step.text)
                if kind == prev_kind:
                    run_len += 1
                    if run_len >= 3:
                        yield Violation(
                            rule=self.rule,
                            message=(
                                f"Scenario {sc.name!r} has {run_len} consecutive "
                                f"{prev_kind}-only steps — insert the missing beat "
                                f"from the other actor or split the story"
                            ),
                            location=self.location(sc.source, f"scenario {sc.name!r}"),
                            severity="warning",
                            hint="After a When, name what the system does back before the next When",
                        )
                        break
                else:
                    run_len = 1
                    prev_kind = kind


if __name__ == "__main__":
    sys.exit(run(AlternateActorEmphasisScanner))
