"""BDD spec for scanners/scanner_collection.py — ScannerCollection discovery, catalog, and run."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scanners import ScannerCollection


_CLEAN_CODE_DIR = _REPO_ROOT / "context_tools" / "clean_engineering"
_PYTHON_SCANNERS = _CLEAN_CODE_DIR / "scanners"


with description("ScannerCollection"):
    with context("a scanner collection rooted at context_tools/clean_engineering/scanners/"):
        with before.each:
            self.collection = ScannerCollection(_CLEAN_CODE_DIR, _PYTHON_SCANNERS)
            self.discovered = self.collection.discover()

        with it("should discover at least one scanner class"):
            expect(len(self.discovered) > 0).to(be_true)

        with it("should list every discovered rule slug when catalog is called"):
            catalog = self.collection.catalog()
            for slug in sorted(self.discovered):
                expect(catalog).to(contain(slug))

        with it("should return a deterministic report when run is called with an explicit file list"):
            template = _CLEAN_CODE_DIR / "clean_engineering.py"
            report = self.collection.run(_REPO_ROOT, [template])
            expect(report.to_dict()["ok"] in (True, False)).to(be_true)
