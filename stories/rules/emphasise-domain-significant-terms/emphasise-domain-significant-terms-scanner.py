"""emphasise-domain-significant-terms — scenario steps use bold/italic emphasis.

Mechanical check on `workspace.scenarios`:
- Each Scenario must have at least one step with a bold concept (`**X**`) or
  italic value (`*v*`). A scenario with entirely plain-prose steps carries
  no domain emphasis and is a smell.

Consistent multi-word Title Case, correct concept vs. value distinction, and
snake_case column mapping are AI-judge territory.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class EmphasiseDomainSignificantTermsScanner(ArtifactScanner):
    """Every scenario has at least one bold or italic term across its steps."""
    rule = "emphasise-domain-significant-terms"
    kind = "quality"
    reads = ("scenarios",)

    def scan(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            clauses = sc.all_clauses
            if not clauses:
                continue
            has_emphasis = any(
                bool(clause.concepts) or bool(clause.values) for clause in clauses
            )
            if not has_emphasis:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Scenario {sc.name!r} has no bold concepts or italic values "
                        f"in any step — domain-significant terms should be emphasised"
                    ),
                    location=self.location(sc.source, f"scenario {sc.name!r}"),
                    severity="warning",
                    hint=(
                        "Wrap domain terms in **bold** (concepts) and *italic* "
                        "(values / instances) — see stories/templates/md/scenario-*.md"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(EmphasiseDomainSignificantTermsScanner))
