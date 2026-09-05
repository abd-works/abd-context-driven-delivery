"""BDD spec — kebab-case-paths scanner."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
_SCANNERS = _REPO / "context_tools" / "stories" / "scanners"
if str(_SCANNERS) not in sys.path:
    sys.path.insert(0, str(_SCANNERS))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from kebab_case_paths_scanner import KebabCasePathsScanner
from context_tools.stories.story_model.source_location import SourceLocation
from context_tools.stories.story_model.story_map import StoryMap
from context_tools.stories.story_model.test_file import Language, TestSuite, Tier
from context_tools.stories.story_model.workspace import Workspace


def _workspace(rel_path: str) -> Workspace:
    suite = TestSuite(
        tier=Tier("front-end"),
        language=Language("py"),
        name="Submit Order",
        source=SourceLocation(file=rel_path),
    )
    return Workspace(root=Path("."), story_map=StoryMap(), test_suites=[suite])


with description("kebab-case-paths") as self:
    with before.each:
        self.scanner = KebabCasePathsScanner("kebab-case-paths")

    with it("should accept kebab epic/sub-epic/story.tier paths"):
        ws = _workspace("manage-orders/place-order/submit-order.front-end.py")
        expect(list(self.scanner.scan_workspace(ws))).to(equal([]))

    with it("should accept a Python epic helper at epic root"):
        ws = _workspace("manage-orders/manage_orders_helper.py")
        expect(list(self.scanner.scan_workspace(ws))).to(equal([]))

    with context("with snake_case folder names"):
        with it("should report a violation"):
            ws = _workspace("Manage_Orders/place-order/submit-order.front-end.py")
            violations = list(self.scanner.scan_workspace(ws))
            expect(len(violations)).to(equal(1))
            expect(violations[0].rule).to(equal("kebab-case-paths"))

    with context("with legacy snake story files"):
        with it("should warn"):
            ws = _workspace("manage-orders/place-order/submit_order_stories.py")
            violations = list(self.scanner.scan_workspace(ws))
            expect(len(violations)).to(equal(1))
            expect(violations[0].severity).to(equal("warning"))
