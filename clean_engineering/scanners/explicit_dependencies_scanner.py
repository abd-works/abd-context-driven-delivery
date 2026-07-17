"""Scanner: detect hidden dependency construction in constructors."""
from pathlib import Path

from code_scanner import CodeScanner


class ExplicitDependenciesScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for oclass, _parsed in self._iter_classes(file_path):
                for op in oclass.operations:
                    if op.name not in {"__init__", "constructor"}:
                        continue
                    for type_name, lineno in op.constructed_types:
                        violations.append(
                            self.violation(
                                f"Hidden dependency '{type_name}()' constructed "
                                f"inside {op.name} in '{oclass.name}'. "
                                "Inject via constructor parameter instead.",
                                location=str(file_path),
                                line=lineno,
                            )
                        )
        return violations


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            ExplicitDependenciesScanner, "use-explicit-dependencies", collect_python_files
        )
    )
