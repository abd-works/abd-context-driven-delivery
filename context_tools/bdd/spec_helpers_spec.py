"""BDD spec for scan fixture-pair helpers — fail file fails scan, pass file passes.

Mistake specs should call these helpers rather than inventing a parallel eval harness.
"""
import sys
import tempfile
from pathlib import Path

from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from context_tools.bdd.spec_helpers import (  # noqa: E402
    expect_scan_fails,
    expect_scan_passes,
)
from scanners import Scan, ScannerCollection  # noqa: E402

_FLAG_FAIL_MARKER_SCANNER = '''
from pathlib import Path

from scanners import Scanner


class FlagFailMarkerScanner(Scanner):
    RULE = "flag-fail-marker"

    def scan_file(self, root: Path, file_path: Path) -> list:
        text = file_path.read_text(encoding="utf-8")
        if "FAIL" in text:
            return [self.violation("fail marker", location=str(file_path))]
        return []
'''


class _MarkerScan(Scan):
    def __init__(self, scanners_dir: Path) -> None:
        self._scanners_dir = scanners_dir

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(
            module_dir=self._scanners_dir, root_path=self._scanners_dir
        )


with description("a scan fixture pair"):
    with before.each:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        scanners_dir = root / "rules"
        scanners_dir.mkdir()
        (scanners_dir / "flag_fail_marker_scanner.py").write_text(
            _FLAG_FAIL_MARKER_SCANNER, encoding="utf-8"
        )
        self.scan = _MarkerScan(scanners_dir)
        self.fail_file = root / "faultyAsset.md"
        self.fail_file.write_text("this asset should FAIL scan\n", encoding="utf-8")
        self.pass_file = root / "repairedAsset.md"
        self.pass_file.write_text("this asset should pass scan\n", encoding="utf-8")

    with context("a file that violates the rule"):
        with it("should fail scan"):
            expect_scan_fails(
                self.scan, self.fail_file, rule="flag-fail-marker", root=self.fail_file.parent
            )

    with context("a file that satisfies the rule"):
        with it("should pass scan"):
            expect_scan_passes(
                self.scan, self.pass_file, rule="flag-fail-marker", root=self.pass_file.parent
            )
