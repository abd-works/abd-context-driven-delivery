"""BDD spec — Stories Python scanners are gone after CodeQL migration."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
for _cat in ("harness", "tools", "practices", "actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from practices.clean_engineering.model.drawio.scanners._drawio_base import ScannerCollection

_STORIES = _REPO / "practices" / "stories"
_SCANNERS = _STORIES / "scanners"


with description("Stories scanner discovery"):
    with it("should have no remaining Python scanners"):
        expect(sorted(ScannerCollection(_STORIES, _SCANNERS).discover())).to(equal([]))
