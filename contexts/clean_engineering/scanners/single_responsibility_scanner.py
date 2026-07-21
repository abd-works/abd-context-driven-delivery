"""Scanner: detect classes with too many public methods or mixed responsibilities."""
from pathlib import Path

from code_scanner import CodeScanner

IO_INDICATORS = {
    "open",
    "read",
    "write",
    "print",
    "println",
    "send",
    "recv",
    "connect",
    "execute",
    "cursor",
}
CALC_INDICATORS = {"sum", "average", "calculate", "compute", "total", "score", "convert", "parse"}

MAX_PUBLIC_METHODS = 10


class SingleResponsibilityScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for oclass, _parsed in self._iter_classes(file_path):
                self._check_class(oclass, file_path, violations)
        return violations

    def _check_class(self, oclass, file_path, violations):
        public = [op for op in oclass.operations if not op.name.startswith("_")]
        if len(public) > MAX_PUBLIC_METHODS:
            violations.append(
                self.violation(
                    f"Class '{oclass.name}' has {len(public)} public methods "
                    f"(max {MAX_PUBLIC_METHODS}). Split responsibilities.",
                    location=str(file_path),
                    line=oclass.line,
                )
            )
        has_io = False
        has_calc = False
        for op in oclass.operations:
            lower_names = {n.lower() for n in op.callees}
            lower_names.add(op.name.lower())
            if lower_names & IO_INDICATORS:
                has_io = True
            if lower_names & CALC_INDICATORS or any(
                ind in op.name.lower() for ind in CALC_INDICATORS
            ):
                has_calc = True
        if has_io and has_calc:
            violations.append(
                self.violation(
                    (
                        f"Class '{oclass.name}' mixes I/O and calculation methods. "
                        "Separate into distinct classes."
                    ),
                    location=str(file_path),
                    line=oclass.line,
                )
            )


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            SingleResponsibilityScanner,
            "keep-classes-single-responsibility",
            collect_python_files,
        )
    )
