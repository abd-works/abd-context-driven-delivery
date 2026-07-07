"""story-context-placement — verify story-context.md sits at the right level.

Reports at most one violation per file: leaf-folder placement first, missing
required sections otherwise. This keeps the fail fixture producing exactly one
violation for clean regression testing.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class StoryContextPlacementScanner(ArtifactScanner):
    """`story-context.md` must sit at an epic/sub-epic root with the expected shape."""

    rule = "story-context-placement"
    kind = "shape"
    reads = ("story_contexts",)

    def scan(self) -> Iterator[Violation]:
        for ctx in self.workspace.story_contexts:
            if ctx.is_leaf_folder:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"story-context.md at {ctx.folder!r} is placed at a leaf folder; "
                        "move it to the parent epic or sub-epic root"
                    ),
                    location=self.location(ctx.source, ctx.folder),
                    severity="error",
                    hint=(
                        "story-context.md aggregates stories below it. A leaf folder has "
                        "no children left to aggregate — put the file one level up."
                    ),
                )
                continue

            missing: list[str] = []
            if not ctx.title:
                missing.append("H1 title")
            if not ctx.has_status:
                missing.append("**Status:**")
            if not ctx.has_stories_in_scope or not ctx.stories_in_scope:
                missing.append("**Stories in scope:** with at least one bullet")
            if missing:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"story-context.md at {ctx.folder!r} is missing: "
                        f"{', '.join(missing)}"
                    ),
                    location=self.location(ctx.source, ctx.folder),
                    severity="error",
                    hint=(
                        "Follow templates/md/story-context.md — H1 + **Status:** + "
                        "**Stories in scope:** with bullets + **Context / notes:**"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(StoryContextPlacementScanner))
