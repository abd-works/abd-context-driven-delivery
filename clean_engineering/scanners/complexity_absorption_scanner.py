"""Scanner: `complexity-absorption` — public operations don't offload config on callers.

Proxy metric: public method parameter count. A public method with more than
four parameters (excluding `self`, `cls`, and defaulted parameters) is a
signal that setup or configuration the module could absorb internally has
been pushed onto callers.

FP profile: MEDIUM. Some genuinely value-typed operations (e.g. a payment
call that requires 5 distinct pieces of transactional data) can be
legitimate. Treat violations as prompts to ask whether a value object should
absorb the parameters, not as automatic failures.
"""
from __future__ import annotations

import ast
from pathlib import Path

from module_scanner import Module, ModuleScanner

MAX_REQUIRED_PARAMETERS = 4


class ComplexityAbsorptionScanner(ModuleScanner):

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        for file_path in module.python_files:
            tree = self.parse_python(file_path)
            if tree is None:
                continue
            for class_node in _classes(tree):
                for method in _public_methods(class_node):
                    required = _required_param_count(method)
                    if required > MAX_REQUIRED_PARAMETERS:
                        violations.append(
                            self.violation(
                                f"Public operation '{class_node.name}.{method.name}' "
                                f"takes {required} required parameters (max "
                                f"{MAX_REQUIRED_PARAMETERS}). Promote related "
                                f"parameters into a value object so the module "
                                f"absorbs configuration instead of demanding it.",
                                location=str(file_path),
                                line=method.lineno,
                            )
                        )
        return violations


def _classes(tree: ast.AST) -> list[ast.ClassDef]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]


def _public_methods(class_node: ast.ClassDef) -> list[ast.FunctionDef]:
    methods: list[ast.FunctionDef] = []
    for node in class_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_") and node.name != "__init__":
            continue
        methods.append(node)
    return methods


def _required_param_count(method: ast.FunctionDef) -> int:
    args = method.args
    positional = [a for a in args.args if a.arg not in {"self", "cls"}]
    positional_only = [a for a in args.posonlyargs if a.arg not in {"self", "cls"}]
    kw_only = list(args.kwonlyargs)
    all_positional = positional_only + positional
    defaulted = len(args.defaults)
    required_positional = max(0, len(all_positional) - defaulted)
    kw_defaults = args.kw_defaults or []
    required_kw = sum(1 for default in kw_defaults if default is None)
    return required_positional + required_kw


if __name__ == "__main__":
    from scanners import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(
            ComplexityAbsorptionScanner,
            "complexity-absorption",
            collect_module_files,
        )
    )
