"""Scanner: bare/swallowed except - reads Operation.bare_except_lines / swallowed_except_lines."""
from pathlib import Path

from code_scanner import CodeScanner


class SwallowedExceptionsScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                for line in op.bare_except_lines:
                    violations.append(
                        self.violation(
                            (
                                "Bare 'except:' catches everything including SystemExit and "
                                "KeyboardInterrupt. Specify the exception type."
                            ),
                            location=str(file_path),
                            line=line,
                        )
                    )
                for line in op.swallowed_except_lines:
                    # pass vs string-literal: same message family as before
                    violations.append(
                        self.violation(
                            "Exception swallowed with 'pass'. Log, re-raise, or handle it.",
                            location=str(file_path),
                            line=line,
                        )
                    )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(SwallowedExceptionsScanner, "never-swallow-exceptions", collect_python_files)
    )
