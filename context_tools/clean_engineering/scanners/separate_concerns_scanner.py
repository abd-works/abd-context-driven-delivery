"""Scanner: I/O mixed with calculation - reads Operation.callees / has_calculation."""
from pathlib import Path

from code_scanner import CodeScanner

IO_CALLS = {
    "open",
    "print",
    "println",
    "printf",
    "input",
    "read",
    "write",
    "readline",
    "readlines",
    "writelines",
    "close",
    "flush",
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "send",
    "recv",
    "read_text",
    "write_text",
    "read_bytes",
    "write_bytes",
}


class SeparateConcernsScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                has_io = any(c in IO_CALLS for c in op.callees)
                if has_io and op.has_calculation:
                    violations.append(
                        self.violation(
                            (
                                f"Function '{op.name}' mixes I/O with computation. "
                                "Split into a pure function and an I/O wrapper."
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
        run_scanner_main(SeparateConcernsScanner, "separate-concerns", collect_python_files)
    )
