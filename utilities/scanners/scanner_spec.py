"""BDD spec for scanners/scanner-behavior.md - Scanner, Violation, execute_scan."""

import tempfile
from pathlib import Path

from expects import be_true, equal, expect
from mamba import before, context, description, it

from scanners import Scanner, Violation, execute_scan

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


with description("execute_scan"):
    with context("a scanner class and explicit file list"):
        with before.each:
            self.temp_dir = tempfile.TemporaryDirectory()
            self.root = Path(self.temp_dir.name)
            self.file_path = self.root / "sample.py"
            self.file_path.write_text("bad\n", encoding="utf-8")

        with it("should delegate to scanner.scan and return violations"):
            violations = execute_scan(_RuleScanner, "example-rule", self.root, [self.file_path])
            expect(len(violations)).to(equal(1))
            expect(violations[0].rule).to(equal("example-rule"))
