"""Scanner: detect deep nesting — reads Operation.nesting_depth."""
from pathlib import Path

from code_scanner import CodeScanner

MAX_NESTING = 3


class SimplifyControlFlowScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                if op.nesting_depth > MAX_NESTING:
                    violations.append(
                        self.violation(
                            f"Function '{op.name}' has nesting depth {op.nesting_depth} "
                            f"(max {MAX_NESTING}). Use guard clauses or early returns.",
                            location=str(file_path),
                            line=op.line,
                        )
                    )
        return violations


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(SimplifyControlFlowScanner, "simplify-control-flow", collect_python_files)
    )
