"""BDD spec for scanners/scanner-behavior.md - Scanner, Violation, execute_scan."""

import tempfile
from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, it

from scanners import (
    Scanner,
    ScannerRunner,
    Violation,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


class _RuleScanner(Scanner):
    pass_example = "value = 1\n"
    fail_example = "value = 1\n"

    def scan_file(self, root: Path, file_path: Path) -> list[Violation]:
        content = file_path.read_text(encoding="utf-8")
        if "bad" in content:
            return [self.violation("example failure", location=str(file_path), line=1)]
        return []


with description("Scanner"):
    with context("a scanner constructed with a rule slug"):
        with before.each:
            self.scanner = _RuleScanner("example-rule")
            self.temp_dir = tempfile.TemporaryDirectory()
            self.root = Path(self.temp_dir.name)
            self.file_path = self.root / "sample.py"
            self.file_path.write_text("good\n", encoding="utf-8")

        with it("should carry that rule slug on violations when scan is called"):
            violations = self.scanner.scan(self.root, [self.file_path])
            expect(violations).to(equal([]))
            self.file_path.write_text("bad\n", encoding="utf-8")
            violations = self.scanner.scan(self.root, [self.file_path])
            expect(violations[0].rule).to(equal("example-rule"))


with description("Violation"):
    with context("a violation created from a scanner"):
        with before.each:
            self.violation = Violation(
                "example-rule",
                "message",
                location="sample.py",
                line=3,
                severity="error",
            )

        with it("should include rule, violation_message, severity, line_number, and location in to_dict"):
            payload = self.violation.to_dict()
            expect(payload["rule"]).to(equal("example-rule"))
            expect(payload["violation_message"]).to(equal("message"))
            expect(payload["severity"]).to(equal("error"))
            expect(payload["line_number"]).to(equal(3))
            expect(payload["location"]).to(equal("sample.py"))


with description("ScannerRunner.execute_scan"):
    with context("a scanner class and explicit file list"):
        with before.each:
            self.temp_dir = tempfile.TemporaryDirectory()
            self.root = Path(self.temp_dir.name)
            self.file_path = self.root / "sample.py"
            self.file_path.write_text("bad\n", encoding="utf-8")

        with it("should delegate to scanner.scan and return violations"):
            violations = ScannerRunner.execute_scan(_RuleScanner, "example-rule", self.root, [self.file_path])
            expect(len(violations)).to(equal(1))
            expect(violations[0].rule).to(equal("example-rule"))


with description("Scanner.filter_scan_files"):
    with context("a file list that includes paths under skipped directories"):
        with it("should exclude any path whose components include a skipped directory name"):
            files = [Path("node_modules/foo.py"), Path("__pycache__/bar.pyc"), Path("src/baz.py")]
            result = Scanner.filter_scan_files(files)
            expect(result).to(equal([Path("src/baz.py")]))

    with context("a file list with no paths under skipped directories"):
        with it("should return all files unchanged"):
            files = [Path("src/a.py"), Path("lib/b.py")]
            result = Scanner.filter_scan_files(files)
            expect(result).to(equal(files))


with description("Scanner.is_skipped_path"):
    with context("a path whose components include a skipped directory name"):
        with it("should return True for a path under node_modules"):
            expect(Scanner.is_skipped_path(Path("node_modules/foo.py"))).to(be_true)

        with it("should return True for a path under __pycache__"):
            expect(Scanner.is_skipped_path(Path("src/__pycache__/bar.pyc"))).to(be_true)

    with context("a path outside all skipped directory names"):
        with it("should return False for a normal source file"):
            expect(Scanner.is_skipped_path(Path("src/module/foo.py"))).to(be_false)

    with context("a repair fixture under examples/"):
        with it("should return False for faultyAsset under examples/"):
            expect(
                Scanner.is_skipped_path(
                    Path("context_tools/stories/examples/invented-stale-status/faultyAsset")
                )
            ).to(be_false)

        with it("should return False for repairedAsset under examples/"):
            expect(
                Scanner.is_skipped_path(
                    Path("examples/invented-competing-command-surface/repairedAsset")
                )
            ).to(be_false)

        with it("should still skip non-fixture files under examples/"):
            expect(
                Scanner.is_skipped_path(Path("examples/md/story-map.md"))
            ).to(be_true)


with description("ScannerRunner.violations_exit_code"):
    with context("a violations list that is empty"):
        with it("should return exit code 0"):
            expect(ScannerRunner.violations_exit_code([])).to(equal(0))

    with context("a violations list with at least one violation"):
        with it("should return exit code 1"):
            v = Violation("rule", "msg")
            expect(ScannerRunner.violations_exit_code([v])).to(equal(1))


with description("ScannerRunner.run_scanner_main"):
    with context("a scanner class and a collect_files that returns no files"):
        with it("should return exit code 0 when no violations are found"):
            result = ScannerRunner.run_scanner_main(_RuleScanner, "example-rule", lambda _: [], argv=[])
            expect(result).to(equal(0))
