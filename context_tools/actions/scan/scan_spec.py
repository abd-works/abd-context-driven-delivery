"""BDD spec for scanners/scan.py - Scan toolset binding."""
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd

import sys
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scan import Scan, ScannerCollection


class _EmptyScan(Scan):
    """Scan binding with no scanner scripts — always returns ok."""

    def _scanner_collection(self) -> ScannerCollection:
        # this kit directory has no *_scanner.py files, so discover() returns {}
        scanners_dir = Path(__file__).parent
        return ScannerCollection(module_dir=scanners_dir, root_path=scanners_dir)


_FLAG_EVERY_FILE_SCANNER = '''
from pathlib import Path

from scan import Scanner


class FlagEveryFileScanner(Scanner):
    """Flags every file handed to it - proves which paths reached the scanners."""

    RULE = "flag-every-file"

    def scan_file(self, root: Path, file_path: Path) -> list:
        return [self.violation("reached", location=str(file_path))]
'''


class _FlaggingScan(Scan):
    """Scan binding whose single rule flags whatever reaches it."""

    def __init__(self, scanners_dir: Path) -> None:
        super().__init__()
        self._scanners_dir = scanners_dir

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(
            module_dir=self._scanners_dir, root_path=self._scanners_dir
        )


with description("Scan"):
    with context("a scan binding with no scanner rules configured"):
        with before.each:
            self.scan = _EmptyScan()

        with it("should return a string containing 'ok' when scan is called with an empty file list"):
            # Arrange / Act
            result = self.scan.scan([])
            # Assert
            expect(result).to(contain("ok"))

        with it("should return a string showing ok as True when scan is called with an empty file list"):
            # Arrange / Act
            result = self.scan.scan([])
            # Assert — no violations means ok is True
            expect(result).to(contain("True"))

    with context("a scan binding asked for a file that sits under examples/"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            root = Path(self.tmp.name)
            scanners_dir = root / "rules"
            scanners_dir.mkdir()
            (scanners_dir / "flag_every_file_scanner.py").write_text(
                _FLAG_EVERY_FILE_SCANNER, encoding="utf-8"
            )
            self.fixture = root / "project" / "examples" / "widget.py"
            self.fixture.parent.mkdir(parents=True)
            self.fixture.write_text("value = 1\n", encoding="utf-8")
            self.scan = _FlaggingScan(scanners_dir)

        with it("should scan the file the caller named"):
            # Act
            result = self.scan.scan([str(self.fixture)])
            # Assert — the caller named it, so examples/ does not hide it
            expect(result).to(contain("flag-every-file"))

        with it("should still skip a neighbour the caller did not name"):
            # Arrange
            neighbour = self.fixture.parent / "other.py"
            neighbour.write_text("value = 2\n", encoding="utf-8")
            # Act
            result = self.scan.scan([str(self.fixture)])
            # Assert
            expect(result).not_to(contain("other.py"))

    with context("a Scan with no host and no collection override"):
        with it("should refuse to scan because there is no rule set"):
            expect(lambda: Scan().scan([])).to(raise_error(ValueError))

    with context("a Scan bound to a host whose collection flags every file"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            root = Path(self.tmp.name)
            scanners_dir = root / "rules"
            scanners_dir.mkdir()
            (scanners_dir / "flag_every_file_scanner.py").write_text(
                _FLAG_EVERY_FILE_SCANNER, encoding="utf-8"
            )
            self.fixture = root / "widget.py"
            self.fixture.write_text("value = 1\n", encoding="utf-8")

            class _Host:
                def __init__(self, module_dir: Path) -> None:
                    self.module_dir = module_dir

                def _scanner_collection(self) -> ScannerCollection:
                    return ScannerCollection(
                        module_dir=self.module_dir, root_path=self.module_dir
                    )

            self.host = _Host(scanners_dir)
            self.scan = Scan.bound_to(self.host)

        with it("should run the host collection against the named path"):
            result = self.scan.scan([str(self.fixture)])
            expect(result).to(contain("flag-every-file"))

        with it("should run each listed context tool collection when tools are passed"):
            class _Kit(Scan):
                def begin(self, tools=None, action=""):
                    return ""

                def end(self):
                    return ""

            result = _Kit().scan(paths=[str(self.fixture)], tools=[self.host])
            expect(result).to(contain("flag-every-file"))


with description("ScanReport"):
    with context("that holds a violation for a Mistake"):
        with it("should match when rule and artifact location agree"):
            from scan.scan import ScanReport
            from types import SimpleNamespace

            report = ScanReport.from_scan(
                '{"ok": False, "violations": '
                '[{"rule": "plain-english-only", "location": "draft.md"}]}'
            )
            mistake = SimpleNamespace(rule="plain-english-only", artifact="draft.md")
            expect(report.matches(mistake)).to(equal(True))

        with it("should not match a different rule"):
            from scan.scan import ScanReport
            from types import SimpleNamespace

            report = ScanReport.from_scan(
                '{"ok": False, "violations": '
                '[{"rule": "plain-english-only", "location": "draft.md"}]}'
            )
            mistake = SimpleNamespace(rule="other-rule", artifact="draft.md")
            expect(report.matches(mistake)).to(equal(False))
