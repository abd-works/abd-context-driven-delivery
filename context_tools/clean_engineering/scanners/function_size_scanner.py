"""Scanner: detect operations exceeding 20 lines — reads Operation.line_count."""
from pathlib import Path

from code_scanner import CodeScanner


class FunctionSizeScanner(CodeScanner):

    MAX_LINES = 20

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                if op.line_count > self.MAX_LINES:
                    violations.append(
                        self.violation(
                            f"Operation '{op.name}' is {op.line_count} lines "
                            f"(max {self.MAX_LINES}). Extract helpers.",
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
            FunctionSizeScanner, "keep-operations-small-focused", collect_python_files
        )
    )
