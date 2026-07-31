"""Scanner: mixed logging/calc or validation/I/O - reads Operation callees/flags."""
from pathlib import Path

from code_scanner import CodeScanner

LOG_CALLS = {
    "print",
    "println",
    "printf",
    "pprint",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "exception",
    "log",
}
IO_CALLS = {
    "open",
    "read",
    "write",
    "readline",
    "readlines",
    "send",
    "recv",
    "get",
    "post",
    "put",
    "delete",
}


class FunctionSingleResponsibilityScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                has_log = any(c in LOG_CALLS for c in op.callees)
                has_io = any(c in IO_CALLS for c in op.callees)
                if has_log and op.has_calculation:
                    violations.append(
                        self.violation(
                            (
                                f"Function '{op.name}' mixes logging with computation. "
                                "Separate the pure logic from observability concerns."
                            ),
                            location=str(file_path),
                            line=op.line,
                        )
                    )
                if op.has_validation and has_io:
                    violations.append(
                        self.violation(
                            (
                                f"Function '{op.name}' mixes validation with I/O. "
                                "Validate in a separate function."
                            ),
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
            FunctionSingleResponsibilityScanner,
            "keep-functions-single-responsibility",
            collect_python_files,
        )
    )
