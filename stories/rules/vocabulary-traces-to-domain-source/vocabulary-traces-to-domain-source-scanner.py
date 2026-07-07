"""vocabulary-traces-to-domain-source — terms in the workspace must trace
to a domain source.

From `vocabulary-traces-to-domain-source.md`:
> Before writing any term, look it up in domain sources.
> Domain sources (read in this order): Domain Specification, Domain Model,
> Domain Language.

Scope:
- The rule is about *tracing* story-map / AC / scenario vocabulary back to
  a domain source. If no domain source exists yet in the workspace (e.g. a
  shaping-fidelity case, where the team is still discovering the language)
  the rule has nothing to trace against — the scanner silently skips.
- When a domain source *does* exist alongside a story map, verifying that
  every term in every story name / step / test identifier appears in that
  source is AI-judge territory — mechanically doable in narrow cases but
  almost always over- or under-flags without human judgment. This scanner
  therefore acts as an applicability gate: it declares the rule read a
  story map, meaning the eval runner will only invoke it once a story map
  is present, and yields no mechanical violations of its own.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_DOMAIN_SOURCE_NAMES = (
    "domain-specification.md",
    "domain-model.md",
    "domain-language.md",
    "domain-glossary.md",
)


class VocabularyTracesScanner(ArtifactScanner):
    """Applicability gate — no mechanical violations of its own.

    Skips silently when no domain source is present in the workspace; the
    rule has nothing to trace against yet. Term-by-term traceability is
    left to the AI judge.
    """
    rule = "vocabulary-traces-to-domain-source"
    kind = "quality"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        import sys as _sys
        if not self.workspace.has_story_map():
            return
        if not self._has_domain_source():
            # No domain source yet — valid at shaping/exploration fidelity.
            # Print a non-blocking note so the AI can surface it to the user.
            print(
                "NOTE vocabulary-traces-to-domain-source: no domain source found "
                "(domain-language.md, domain-model.md, or domain-specification.md) — "
                "vocabulary tracing is not yet possible; add one when the domain language "
                "is stable enough to be written down.",
                file=_sys.stderr,
            )
            return
        # Term-by-term traceability is AI-judge territory; no further mechanical checks.
        return
        yield  # pragma: no cover - keeps method a generator

    def _has_domain_source(self) -> bool:
        for name in _DOMAIN_SOURCE_NAMES:
            for candidate in self.workspace.root.rglob(name):
                if candidate.is_file():
                    return True
        return False


if __name__ == "__main__":
    sys.exit(run(VocabularyTracesScanner))
