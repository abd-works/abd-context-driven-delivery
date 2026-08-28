"""BDD: CE // comments are invariants and sequencing notes, not prose."""

import sys
import tempfile
from pathlib import Path

from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from context_tools.bdd.spec_helpers import (  # noqa: E402
    expect_scan_fails,
    expect_scan_passes,
)
from scan import Scan, ScannerCollection  # noqa: E402

_SCANNERS = Path(__file__).resolve().parent
_RULE = "ce-comments-are-for-invariants-and-sequencing-notes-only"

_FAULTY = (
    "SelectedPlan\n"
    "  // transient value object - carries chosen Plan into Create Account; no persistence\n"
    "  // two atoms: onboarding 'selected-plan' vs selfcare root 'my-selected-plan'"
    " - same concept, split namespace\n"
)

_REPAIRED = """\
SelectedPlan
  // must not persist across sessions
  // after Create Account, drop the selection
"""


class _CeScan(Scan):
    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(module_dir=_SCANNERS, root_path=_SCANNERS)


with description("ce-comments-are-for-invariants-and-sequencing-notes-only"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.scan = _CeScan()

    with context("a sketch class with descriptive // prose comments"):
        with before.each:
            self.path = self.root / "cdd-sketch.md"
            self.path.write_text(_FAULTY, encoding="utf-8")

        with it("should fail scan"):
            expect_scan_fails(self.scan, self.path, rule=_RULE, root=self.root)

    with context("a sketch class with invariant and sequencing // notes"):
        with before.each:
            self.path = self.root / "cdd-sketch.md"
            self.path.write_text(_REPAIRED, encoding="utf-8")

        with it("should pass scan"):
            expect_scan_passes(self.scan, self.path, rule=_RULE, root=self.root)
