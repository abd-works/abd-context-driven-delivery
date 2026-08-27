"""Scanner: mixed snake_case / camelCase - reads Operation.name."""
import re
from pathlib import Path

from code_scanner import CodeScanner

SNAKE_CASE = re.compile(r"^_*[a-z][a-z0-9]*(_[a-z0-9]+)*_*$")
CAMEL_CASE = re.compile(r"^_*[a-z]+[A-Z][a-zA-Z0-9]*$")
DUNDER = re.compile(r"^__[a-z]+__$")
SKIP_NAMES = {"setUp", "tearDown", "setUpClass", "tearDownClass", "setUpModule"}


class ConsistentNamingScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            snake_ops = []
            camel_ops = []
            for op, _parsed in self._iter_operations(file_path):
                name = op.name
                if name in SKIP_NAMES or DUNDER.match(name):
                    continue
                if CAMEL_CASE.match(name):
                    camel_ops.append(op)
                elif SNAKE_CASE.match(name):
                    snake_ops.append(op)
            if snake_ops and camel_ops:
                minority = camel_ops if len(camel_ops) <= len(snake_ops) else snake_ops
                style = "camelCase" if minority is camel_ops else "snake_case"
                for op in minority:
                    violations.append(
                        self.violation(
                            (
                                f"Function '{op.name}' uses {style} while the file "
                                "majority uses the other convention. Be consistent."
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
        run_scanner_main(ConsistentNamingScanner, "use-consistent-naming", collect_python_files)
    )
