"""BDD spec — Stories scanners discover and run against discovery fixtures."""

import sys
from pathlib import Path

from expects import be_true, equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scanners import ScannerCollection

_STORIES = _REPO / "contexts" / "stories"
_SCANNERS = _STORIES / "scanners"
_PASS = _STORIES / "evals" / "discovery" / "pass" / "verb-noun-map"
_FAIL = _STORIES / "evals" / "discovery" / "fail" / "actor-in-story-name"


with description("Stories scanner discovery"):
    with before.all:
        self.discovered = ScannerCollection(_STORIES, _SCANNERS).discover()

    with it("should discover every ported rule scanner"):
        expect(len(self.discovered) >= 32).to(be_true)

    with it("should include verb-noun-format and four-to-nine-children"):
        expect("verb-noun-format" in self.discovered).to(be_true)
        expect("four-to-nine-children" in self.discovered).to(be_true)


with description("Stories scanners against discovery fixtures"):
    with context("a pass fixture with verb-noun story names"):
        with before.each:
            coll = ScannerCollection(_STORIES, _SCANNERS)
            self.report = coll.run(_PASS, [ _PASS / "story-map.md" ])

        with it("should not report verb-noun-format violations"):
            vn = [v for v in self.report.violations if v.rule == "verb-noun-format"]
            expect(vn).to(equal([]))

    with context("a fail fixture with an actor-led story name"):
        with before.each:
            coll = ScannerCollection(_STORIES, _SCANNERS)
            self.report = coll.run(_FAIL, [ _FAIL / "story-map.md" ])

        with it("should report at least one verb-noun-format violation"):
            vn = [v for v in self.report.violations if v.rule == "verb-noun-format"]
            expect(len(vn) >= 1).to(be_true)
