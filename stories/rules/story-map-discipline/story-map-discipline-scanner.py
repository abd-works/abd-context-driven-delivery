"""story-map-discipline — the map must carry scope boundaries.

Mechanical checks (from `story-map-discipline.md`):
- The story-map source has a `## Scope boundary` section.
- That section names both `**In scope:**` and `**Out of scope:**`.

The other three disciplines (evidence-based, precise, analysed-before-grouped)
are AI-judge territory:
- Evidence-based is partially handled by `brownfield-story-mapping-scanner.py`
  via the `**UNVERIFIED**` marker.
- Precise is handled by `verb-noun-format-scanner.py`.
- Analysed-before-grouped needs review, not a scanner.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class StoryMapDisciplineScanner(ArtifactScanner):
    """The story map has an explicit scope boundary section."""
    rule = "story-map-discipline"
    kind = "quality"
    reads = ("story_map",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return

        # Prefer the markdown story-map — it's the human-readable source that
        # carries prose sections such as ## Scope boundary.  Falling back to
        # whatever `source.file` says is wrong when the workspace was loaded
        # from JSON (story-graph.json), because JSON lacks those prose sections.
        md_candidate = self.workspace.root / "story-map.md"
        if md_candidate.exists():
            source_path = md_candidate
        else:
            source = getattr(self.workspace.story_map, "source", None)
            if source is None:
                return
            source_path = self.workspace.root / source.file
            if not source_path.exists():
                return

        text = source_path.read_text(encoding="utf-8", errors="replace")
        location = source_path.relative_to(self.workspace.root).as_posix() + ":1"

        has_section = "## Scope boundary" in text
        has_in_scope = "**In scope:**" in text
        has_out_scope = "**Out of scope:**" in text

        if not has_section:
            yield Violation(
                rule=self.rule,
                message="Story map has no '## Scope boundary' section",
                location=location,
                severity="warning",
                hint=(
                    "Add a `## Scope boundary` section listing `**In scope:**` "
                    "and `**Out of scope:**` — every node in the map must trace "
                    "to what the user asked for"
                ),
            )
            return

        if not (has_in_scope and has_out_scope):
            missing = []
            if not has_in_scope:
                missing.append("**In scope:**")
            if not has_out_scope:
                missing.append("**Out of scope:**")
            yield Violation(
                rule=self.rule,
                message=(
                    f"Scope boundary is present but missing: {', '.join(missing)}"
                ),
                location=location,
                severity="warning",
                hint=(
                    "A scope boundary needs both an `**In scope:**` list and "
                    "an `**Out of scope:**` list — the latter tracks scope drift"
                ),
            )


if __name__ == "__main__":
    sys.exit(run(StoryMapDisciplineScanner))
