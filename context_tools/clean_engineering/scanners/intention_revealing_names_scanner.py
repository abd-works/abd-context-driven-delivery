"""Scanner: vague/short names - reads Operation.assigned_names / parameters / loop targets."""
from pathlib import Path

from code_scanner import CodeScanner

LOOP_VARS = {"i", "j", "k", "n", "x", "y", "z", "_", "__"}
GENERIC_NAMES = {
    "info",
    "thing",
    "stuff",
    "temp",
    "tmp",
    "val",
    "obj",
    "item",
    "foo",
    "bar",
    "baz",
    "misc",
    "blob",
    "value",
}
MIN_NAME_LENGTH = 3


class IntentionRevealingNamesScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                loop_targets = set(op.loop_target_names)
                seen: set[tuple[str, int]] = set()
                for name, lineno in op.assigned_names:
                    key = (name, lineno)
                    if key in seen:
                        continue
                    seen.add(key)
                    self._check_name(name, lineno, loop_targets, file_path, violations)
        return violations

    def _check_name(self, name, lineno, loop_targets, file_path, violations):
        if name.startswith("_"):
            return
        if name.lower() in GENERIC_NAMES:
            violations.append(
                self.violation(
                    f"Name '{name}' is too generic. Use a domain-specific name.",
                    location=str(file_path),
                    line=lineno,
                )
            )
            return
        if len(name) == 1 and name not in LOOP_VARS:
            violations.append(
                self.violation(
                    f"Single-letter name '{name}' hides intention.",
                    location=str(file_path),
                    line=lineno,
                )
            )
        elif (
            1 < len(name) < MIN_NAME_LENGTH
            and name not in LOOP_VARS
            and (name, lineno) not in loop_targets
        ):
            violations.append(
                self.violation(
                    f"Name '{name}' is very short ({len(name)} chars). Use a descriptive name.",
                    location=str(file_path),
                    line=lineno,
                )
            )


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            IntentionRevealingNamesScanner, "use-intention-revealing-names", collect_python_files
        )
    )
