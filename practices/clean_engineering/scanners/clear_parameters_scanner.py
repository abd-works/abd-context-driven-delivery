"""Scanner: too many or vague parameters - reads Operation.param_count / parameters."""
from pathlib import Path

from code_scanner import CodeScanner

MAX_PARAMS = 5
MAX_INIT_PARAMS = 7
VAGUE_NAMES = {
    "thing",
    "stuff",
    "info",
    "data",
    "args_list",
    "params",
    "options",
    "misc",
    "obj",
    "payload",
}


class ClearParametersScanner(CodeScanner):

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            for op, _parsed in self._iter_operations(file_path):
                limit = (
                    MAX_INIT_PARAMS
                    if op.name in {"__init__", "constructor"}
                    else MAX_PARAMS
                )
                if op.param_count > limit:
                    violations.append(
                        self.violation(
                            f"Function '{op.name}' has {op.param_count} parameters "
                            f"(max {limit}). Group related params into an object.",
                            location=str(file_path),
                            line=op.line,
                        )
                    )
                for arg_name in op.parameters:
                    if arg_name.lower() in VAGUE_NAMES:
                        violations.append(
                            self.violation(
                                (
                                    f"Parameter '{arg_name}' in '{op.name}' is vague. "
                                    "Use a domain-specific name."
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
        run_scanner_main(
            ClearParametersScanner, "use-clear-function-parameters", collect_python_files
        )
    )
