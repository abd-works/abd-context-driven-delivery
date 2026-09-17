"""Scanner: generic class/method names - reads OoadClass.name / Operation.name."""
from pathlib import Path

from code_scanner import CodeScanner

GENERIC_CLASS_NAMES = {
    "Manager",
    "Handler",
    "Helper",
    "Util",
    "Utils",
    "Processor",
    "Service",
    "Controller",
    "Base",
}
GENERIC_METHOD_NAMES = {
    "process",
    "handle",
    "execute",
    "run",
    "do",
    "perform",
    "manage",
}


class DomainLanguageCodeScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for oclass, _parsed in self._iter_classes(file_path):
                if oclass.name in GENERIC_CLASS_NAMES:
                    violations.append(
                        self.violation(
                            (
                                f"Class '{oclass.name}' is a generic name. "
                                "Use a domain entity name instead."
                            ),
                            location=str(file_path),
                            line=oclass.line,
                        )
                    )
            for op, _parsed in self._iter_operations(file_path):
                if op.name in GENERIC_METHOD_NAMES:
                    violations.append(
                        self.violation(
                            (
                                f"Method '{op.name}' is too generic. "
                                "Use a domain responsibility verb."
                            ),
                            location=str(file_path),
                            line=op.line,
                        )
                    )
        return violations


if __name__ == "__main__":
    from scan import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(DomainLanguageCodeScanner, "use-domain-language", collect_python_files)
    )
