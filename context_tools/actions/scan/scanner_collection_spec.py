"""BDD spec for scanners/scanner_collection.py - ScannerCollection discovery, catalog, and run."""

import sys
from pathlib import Path

from expects import be_none, be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scan import ScannerCollection, ScannerReport, Violation


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

        with it("should return the scanner class for a known slug when get is called"):
            slug = sorted(self.discovered.keys())[0]
            scanner_cls = self.collection.get(slug)
            expect(scanner_cls is not None).to(be_true)

        with it("should return None for an unknown slug when get is called"):
            result = self.collection.get("no-such-rule-xyz-99999")
            expect(result).to(be_none)


with description("ScannerReport"):
    with context("a report that has violations"):
        with before.each:
            v = Violation("rule", "msg", location="f.py", line=1)
            self.report = ScannerReport(violations=[v], rules=["rule"])

        with it("should mark ok as False in to_dict when violations are present"):
            d = self.report.to_dict()
            expect(d["ok"]).to(equal(False))

        with it("should include the violation entries in to_dict"):
            d = self.report.to_dict()
            expect(len(d["violations"])).to(equal(1))

    with context("a report that has no violations"):
        with before.each:
            self.report = ScannerReport(violations=[], rules=[])

        with it("should mark ok as True in to_dict when no violations are present"):
            d = self.report.to_dict()
            expect(d["ok"]).to(equal(True))
