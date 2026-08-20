"""BDD: generated module markdown must not leak template annotation comments."""

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
from scanners import Scan, ScannerCollection  # noqa: E402

_SCANNERS = Path(__file__).resolve().parent

_FAULTY_MU = """\
# config <!-- Mu -->
- **Purpose:** Owns runtime flags.
"""

_FAULTY_BLANK = """\
# config

- **Purpose:** Owns runtime flags.
- **Seam (terms):** Config
"""

_REPAIRED = """\
# config
- **Purpose:** Owns runtime flags.
- **Seam (terms):** Config
"""


class _CeScan(Scan):
    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(module_dir=_SCANNERS, root_path=_SCANNERS)


with description("output-format scanner"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.scan = _CeScan()

    with context("a module summary that still has <!-- Mu --> comments"):
        with before.each:
            self.path = self.root / "pml-my-modules.md"
            self.path.write_text(_FAULTY_MU, encoding="utf-8")

        with it("should fail scan"):
            expect_scan_fails(
                self.scan, self.path, rule="output-format", root=self.root
            )

    with context("a module summary with a blank line between heading and purpose"):
        with before.each:
            self.path = self.root / "pml-my-modules.md"
            self.path.write_text(_FAULTY_BLANK, encoding="utf-8")

        with it("should fail scan"):
            expect_scan_fails(
                self.scan, self.path, rule="output-format", root=self.root
            )

    with context("a module summary with no annotation comments and tight headings"):
        with before.each:
            self.path = self.root / "pml-my-modules.md"
            self.path.write_text(_REPAIRED, encoding="utf-8")

        with it("should pass scan"):
            expect_scan_passes(
                self.scan, self.path, rule="output-format", root=self.root
            )
