"""Scanner: detect magic numbers and numbered variable names."""
import re
from pathlib import Path

from code_scanner import CodeScanner

WELL_KNOWN_MAGIC = {
    200, 201, 204, 301, 302, 400, 401, 403, 404, 405, 409, 422, 429, 500, 502, 503,
    60, 3600, 86400, 604800,
    1024, 2048, 4096, 8192,
}
NUMBERED_VAR = re.compile(r"^[a-z]+\d+$")


class MeaningfulContextScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                for value, lineno in op.magic_numbers:
                    if value in WELL_KNOWN_MAGIC or int(value) in WELL_KNOWN_MAGIC:
                        violations.append(
                            self.violation(
                                f"Magic number {value} used inline. "
                                "Extract to a named constant.",
                                location=str(file_path),
                                line=lineno,
                            )
                        )
                for name, lineno in op.assigned_names:
                    if NUMBERED_VAR.match(name):
                        violations.append(
                            self.violation(
                                f"Numbered variable '{name}' lacks meaningful context. "
                                "Use a descriptive name.",
                                location=str(file_path),
                                line=lineno,
                            )
                        )
                for name in op.parameters:
                    if NUMBERED_VAR.match(name):
                        violations.append(
                            self.violation(
                                f"Numbered variable '{name}' lacks meaningful context. "
                                "Use a descriptive name.",
                                location=str(file_path),
                                line=op.line,
                            )
                        )
        return violations


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            MeaningfulContextScanner, "provide-meaningful-context", collect_python_files
        )
    )
