"""Scanner: high-level ops mixing low-level I/O — reads Operation.callees / literals."""
from pathlib import Path

from code_scanner import CodeScanner

HIGH_LEVEL_NAMES = {
    "orchestrate",
    "coordinate",
    "process",
    "handle",
    "dispatch",
    "workflow",
    "pipeline",
}
LOW_LEVEL_CALLS = {
    "open",
    "read",
    "write",
    "cursor",
    "execute",
    "connect",
    "socket",
    "recv",
    "send",
    "read_text",
    "write_text",
    "read_bytes",
    "write_bytes",
    "executemany",
    "fetchone",
    "fetchall",
}
SQL_STRINGS = {"SELECT", "INSERT", "UPDATE", "DELETE", "CREATE TABLE", "DROP"}


class AbstractionLevelsScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                if not any(kw in op.name.lower() for kw in HIGH_LEVEL_NAMES):
                    continue
                has_low = any(c in LOW_LEVEL_CALLS for c in op.callees)
                if not has_low:
                    for lit in op.literals:
                        upper = lit.upper().lstrip()
                        if any(upper.startswith(kw) for kw in SQL_STRINGS):
                            has_low = True
                            break
                if has_low:
                    violations.append(
                        self.violation(
                            (
                                f"Function '{op.name}' mixes high-level orchestration with "
                                "low-level I/O. Delegate I/O to a separate function."
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
            AbstractionLevelsScanner, "maintain-abstraction-levels", collect_python_files
        )
    )
