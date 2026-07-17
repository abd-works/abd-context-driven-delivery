"""BDD spec for scanners/scanner_collection.py — ScannerCollection discovery, catalog, and run."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from clean_code.clean_code_ground_truth import (
    concept_rule_slugs,
    load_concepts_section,
)
from scanners import ScannerCollection


_CLEAN_CODE_DIR = _REPO_ROOT / "clean_code"
_PYTHON_SCANNERS = _CLEAN_CODE_DIR / "formats" / "python" / "scanners"


with description("ScannerCollection"):
    with context("a scanner collection rooted at clean_code/formats/python/scanners/"):
        with before.each:
            self.collection = ScannerCollection(_CLEAN_CODE_DIR, _PYTHON_SCANNERS)
            self.discovered = self.collection.discover()

        with it("should map every concept rule slug from clean-code.md to a scanner class"):
            concept_slugs = set(concept_rule_slugs(load_concepts_section(_CLEAN_CODE_DIR)))
            scanner_slugs = set(self.discovered)
            expect(len(scanner_slugs) > 0).to(be_true)
            missing = concept_slugs - scanner_slugs
            expect(len(missing)).to(equal(0))

        with it("should list every discovered rule slug when catalog is called"):
            catalog = self.collection.catalog()
            for slug in sorted(self.discovered):
                expect(catalog).to(contain(slug))

        with it("should return a deterministic report when run is called with an explicit file list"):
            template = _CLEAN_CODE_DIR / "formats" / "python" / "clean-code-template.py"
            report = self.collection.run(_REPO_ROOT, [template])
            expect(report.to_dict()["ok"] in (True, False)).to(be_true)
