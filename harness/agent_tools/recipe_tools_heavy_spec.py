"""A recipe (an ``@agent_instructions`` body) names each of its own tools through ``tools(self.tool)``.

Written bare, ``self.tool()`` is run while the recipe is expanded: a tool that needs arguments raises
``RecipeLineFailed``, and one that does not does its work, such as writing a file, every time the instructions are read.
"""

import ast
from pathlib import Path

from expects import be_empty, expect
from mamba import description, it

_REPO = Path(__file__).resolve().parents[2]
_PACKAGES = ("harness", "space", "tools", "cdd_guidance")
_NOT_SOURCE = {"retired", "node_modules", "__pycache__", "templates", "seeds", "fixtures", "sandbox", "app"}


def _decorator_names(function: ast.FunctionDef) -> set[str]:
    names = set()
    for decorator in function.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        names.add(target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", ""))
    return names


def _bare_tool_calls(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    found = []
    for owner in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
        methods = [node for node in owner.body if isinstance(node, ast.FunctionDef)]
        tool_names = {method.name for method in methods if "agent_tool" in _decorator_names(method)}
        for recipe in (method for method in methods if "agent_instructions" in _decorator_names(method)):
            for statement in ast.walk(recipe):
                call = statement.value if isinstance(statement, ast.Expr) else None
                if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)):
                    continue
                if isinstance(call.func.value, ast.Name) and call.func.value.id == "self" and call.func.attr in tool_names:
                    found.append(f"{path.relative_to(_REPO).as_posix()}:{statement.lineno} self.{call.func.attr}()")
    return found


def _source_files() -> list[Path]:
    files = []
    for package in _PACKAGES:
        for path in sorted((_REPO / package).rglob("*.py")):
            if not any(part in _NOT_SOURCE or part.startswith(".") for part in path.relative_to(_REPO).parts[:-1]):
                files.append(path)
    return files


with description("the recipes in the repository"):
    with it("should name each of their own tools through tools(...) rather than call it"):
        expect([line for path in _source_files() for line in _bare_tool_calls(path)]).to(be_empty)
