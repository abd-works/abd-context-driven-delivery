"""BDD spec — UX Python scanners are gone."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
for _cat in ("tools", "practices", "actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from practices.clean_engineering.model.drawio.scanners._drawio_base import ScannerCollection

_UX = _REPO / "practices" / "ux"
_SCANNERS = _UX / "scanners"


with description("UX scanner discovery"):
    with it("should have no remaining Python scanners"):
        expect(sorted(ScannerCollection(_UX, _SCANNERS).discover())).to(equal([]))
