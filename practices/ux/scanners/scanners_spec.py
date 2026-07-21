"""BDD spec — UX scanners discover against the UX package."""

import sys
from pathlib import Path

from expects import be_true, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scanners import ScannerCollection

_UX = _REPO / "ux"
_SCANNERS = _UX / "scanners"


with description("UX scanner discovery"):
    with before.all:
        self.discovered = ScannerCollection(_UX, _SCANNERS).discover()

    with it("should discover core UX scanners"):
        for slug in (
            "tab-states-are-separate-screens",
            "screen-story-budget",
            "ia-named-regions-only",
            "screen-names-use-domain-terms",
            "story-domain-js-imported",
        ):
            expect(slug in self.discovered).to(be_true)
