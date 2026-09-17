"""Scanner: private module-level functions called from only one class should be methods.

Rule: prefer-class-operations

A private module-level function is a detached method when every call site in the
same file lives inside exactly one class. The logic belongs on that class — not
floating at the module level — so callers see behaviour through named operations
rather than reaching past the class to a free-floating helper.
"""
import ast
from pathlib import Path

from code_scanner import CodeScanner


class PreferClassOperationsScanner(CodeScanner):
    """Flag private module-level functions called exclusively from one class."""

    def scan(self, root: Path, files: list[Path]) -> list:
        violations = []
        for file_path in files:
            violations.extend(self._scan_file(file_path))
        return violations

    def _scan_file(self, file_path: Path) -> list:
        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return []
        module_privates = self._module_private_functions(tree)
        if not module_privates:
            return []
        sole_owner = self._sole_calling_class(tree, {n for n, _ in module_privates})
        return [
            self.violation(
                f"Module-level function '{fn}' is only called from '{sole_owner[fn]}'. "
                f"Move it to '{sole_owner[fn]}' as a private method.",
                location=str(file_path),
                line=lineno,
            )
            for fn, lineno in module_privates
            if fn in sole_owner
        ]

    @staticmethod
    def _module_private_functions(tree: ast.Module) -> list[tuple[str, int]]:
        """Private functions defined at module scope (not inside any class)."""
        return [
            (node.name, node.lineno)
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("_")
        ]

    @staticmethod
    def _sole_calling_class(tree: ast.Module, fn_names: set[str]) -> dict[str, str]:
        """Return {fn_name: class_name} for functions called from exactly one class."""
        class_calls: dict[str, set[str]] = {}
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Name)
                    and child.func.id in fn_names
                ):
                    class_calls.setdefault(child.func.id, set()).add(node.name)
        return {
            fn: next(iter(classes))
            for fn, classes in class_calls.items()
            if len(classes) == 1
        }


if __name__ == "__main__":
    from scan import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            PreferClassOperationsScanner,
            "prefer-class-operations",
            collect_python_files,
        )
    )
