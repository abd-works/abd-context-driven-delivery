"""Scanner: bare/pass except - reads Operation except line lists."""
from pathlib import Path

from code_scanner import CodeScanner


class ExceptionHandlingScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                for line in op.bare_except_lines:
                    violations.append(
                        self.violation(
                            (
                                "Bare 'except:' catches all exceptions including SystemExit. "
                                "Use 'except SpecificError:'."
                            ),
                            location=str(file_path),
                            line=line,
                        )
                    )
                for line in op.swallowed_except_lines:
                    if line in op.bare_except_lines:
                        continue
                    violations.append(
                        self.violation(
                            "Exception swallowed silently with 'pass'. Log or re-raise.",
                            location=str(file_path),
                            line=line,
                        )
                    )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(ExceptionHandlingScanner, "use-exceptions-properly", collect_python_files)
    )
