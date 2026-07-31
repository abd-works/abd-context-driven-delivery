"""Scanner: encapsulation - public fields, leaked mutables, missing property."""
from pathlib import Path

from code_scanner import CodeScanner

PROPERTY_PREFIXES = ("calculate_", "compute_", "get_")


class PropertyEncapsulationCodeScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for oclass, _parsed in self._iter_classes(file_path):
                self._check_class(oclass, file_path, violations)
        return violations

    def _check_class(self, oclass, file_path, violations):
        property_names = {op.name for op in oclass.operations if op.is_property}
        for op in oclass.operations:
            if op.name in {"__init__", "constructor"}:
                for attr, lineno in op.public_attr_assigns:
                    violations.append(
                        self.violation(
                            (
                                f"Public attribute '{attr}' in '{oclass.name}.{op.name}'. "
                                "Prefix with '_' and expose via a property/getter."
                            ),
                            location=str(file_path),
                            line=lineno,
                        )
                    )
            if op.name in property_names:
                continue
            if any(op.name.startswith(p) for p in PROPERTY_PREFIXES) and op.param_count == 0:
                violations.append(
                    self.violation(
                        (
                            f"Method '{op.name}' in '{oclass.name}' takes no args "
                            "beyond self - use a property/getter."
                        ),
                        location=str(file_path),
                        line=op.line,
                    )
                )
            if op.returns_private_attr and not op.is_property:
                violations.append(
                    self.violation(
                        (
                            f"Method '{op.name}' returns mutable internal "
                            "private attribute directly. Return a copy."
                        ),
                        location=str(file_path),
                        line=op.line,
                    )
                )


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            PropertyEncapsulationCodeScanner, "enforce-encapsulation", collect_python_files
        )
    )
