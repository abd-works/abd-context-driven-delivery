"""Spec support: run Stories graph rules on example story tests the way validate runs them.

An example is a folder of story tests in the layout a build reads (`tests/<epic>/<sub-epic>_story.test.ts`). The
folder is read through the real working-copy build, so Stories' own TypeScript format reads each story test into the
story map and every node carries the type and facts a live build gives it. Each rule then runs through the practice's
schema, so a rule the schema never applies to a node type finds nothing there and its example fails.
"""

from __future__ import annotations

from pathlib import Path

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.stories.rules import BY_SLUG
from cdd_guidance.practices.stories.stories import Stories

_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "typescript" / "_examples"


def stories_fixture(folder: Path) -> RuleFixture:
    """The files under folder, named from it, read by Stories as a live load reads a working copy."""
    files = {path.relative_to(folder).as_posix(): path.read_text(encoding="utf-8") for path in folder.rglob("*") if path.is_file()}
    return RuleFixture(Stories, files)


def assert_stories_example_pair(slug: str) -> None:
    """The rule flags the story tests of its example's faulty folder and passes those of its repaired one."""
    root = _EXAMPLES / slug
    RulePair(BY_SLUG[slug], stories_fixture(root / "faulty"), stories_fixture(root / "repaired")).check()
