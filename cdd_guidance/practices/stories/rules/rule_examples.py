"""Spec support: run Stories graph rules on example story tests the way validate runs them.

An example is a folder of story tests in the layout a build reads (`tests/<epic>/<sub-epic>_story.test.ts`). The
folder is read through the real working-copy build, so Stories' own TypeScript format reads each story test into the
story map and every node carries the type and facts a live build gives it. Each rule then runs through the practice's
schema, so a rule the schema never applies to a node type finds nothing there and its example fails. An example that
holds a domain model document (`domain-model.md`) is read with DDD beside Stories, so a rule that applies only where a
model is written, such as then-observes-an-example, has the model its example links to.
"""

from __future__ import annotations

from pathlib import Path

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.rules import BY_SLUG
from cdd_guidance.practices.stories.stories import Stories

_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "typescript" / "_examples"
_DOMAIN_MODEL_FILE = "domain-model.md"


def stories_fixture(folder: Path) -> RuleFixture:
    """The files under folder, named from it, read by Stories as a live load reads a working copy."""
    files = {path.relative_to(folder).as_posix(): path.read_text(encoding="utf-8") for path in folder.rglob("*") if path.is_file()}
    models = (Ddd,) if any(Path(file).name == _DOMAIN_MODEL_FILE for file in files) else ()
    return RuleFixture(Stories, files, beside=models)


def assert_stories_example_pair(slug: str) -> None:
    """The rule flags the story tests of its example's faulty folder and passes those of its repaired one."""
    root = _EXAMPLES / slug
    RulePair(BY_SLUG[slug], stories_fixture(root / "faulty"), stories_fixture(root / "repaired")).check()
