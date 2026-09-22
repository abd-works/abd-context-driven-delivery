"""BDD spec - artifacts-mirror-story-hierarchy accepts `{story}_story.test.ts`."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
_SCANNERS = _REPO / "practices" / "stories" / "scanners"
if str(_SCANNERS) not in sys.path:
    sys.path.insert(0, str(_SCANNERS))
for _cat in ("tools", "practices", "actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from artifacts_mirror_story_hierarchy_scanner import ArtifactsMirrorStoryHierarchyScanner
from practices.stories.model.nodes import Epic, Story, SubEpic
from practices.stories.model.source_location import SourceLocation
from practices.stories.model.story_map import StoryMap
from practices.stories.model.test_file import Language, TestSuite, Tier
from practices.stories.model.workspace import Workspace


def _workspace_with_suite(rel_path: str) -> Workspace:
    story_map = StoryMap()
    epic = Epic("Manage Orders", 1)
    sub = SubEpic("Place Order", 1)
    sub.stories.append(Story("Submit Order", 1))
    epic.sub_epics.append(sub)
    story_map.append_epic(epic)
    suite = TestSuite(
        tier=Tier(""),
        language=Language("ts"),
        name="Submit Order",
        source=SourceLocation(file=rel_path),
    )
    return Workspace(
        root=Path("."),
        story_map=story_map,
        test_suites=[suite],
    )


with description("artifacts-mirror-story-hierarchy") as self:
    with before.each:
        self.scanner = ArtifactsMirrorStoryHierarchyScanner(
            "artifacts-mirror-story-hierarchy"
        )

    with context("a GWT file named `{story}_story.test.ts` under epic/sub-epic/story"):
        with it("should accept the file in the story folder"):
            workspace = _workspace_with_suite(
                "tests/manage-orders/place-order/submit-order/submit_order_story.test.ts"
            )
            violations = list(self.scanner.scan_workspace(workspace))
            expect(violations).to(equal([]))
