"""Scanner: detect duplicate function bodies via Operation.body_fingerprint."""
from pathlib import Path

from code_scanner import CodeScanner

MIN_LINES = 3


class DuplicationScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        seen: dict[str, tuple[str, str, int | None]] = {}
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                if op.line_count < MIN_LINES or not op.body_fingerprint:
                    continue
                key = op.body_fingerprint
                if key in seen:
                    orig_name, orig_file, orig_line = seen[key]
                    violations.append(
                        self.violation(
                            f"Function '{op.name}' has the same body as "
                            f"'{orig_name}' ({orig_file}:{orig_line}). "
                            "Extract shared logic.",
                            location=str(file_path),
                            line=op.line,
                        )
                    )
                else:
                    seen[key] = (op.name, str(file_path), op.line)
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(DuplicationScanner, "eliminate-duplication", collect_python_files)
    )
