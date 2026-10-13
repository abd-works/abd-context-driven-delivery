"""Rule-oriented facts extracted from operation bodies — shared by parsers."""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from practices.clean_engineering.model.operation import Operation

_CATCH = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{")
_PY_EXCEPT = re.compile(r"\bexcept\s*(?::|\([^)]*\)\s*:)")
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_NUMBER = re.compile(r"\b(\d+(?:\.\d+)?)\b")
_SAFE_NUMBERS = {0, 1, 2, -1, 0.0, 1.0, 0.5, 10, 100}


def _brace_body(text: str, open_index: int) -> str | None:
    if open_index >= len(text) or text[open_index] != "{":
        return None
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[open_index + 1 : index]
    return None


def _brace_depth(text: str) -> int:
    depth = 0
    deepest = 0
    for character in text:
        if character == "{":
            depth += 1
            deepest = max(deepest, depth)
        elif character == "}":
            depth = max(0, depth - 1)
    return deepest


def control_flow_depth_in_text(text: str) -> int:
    """Nested if/for/while — Python indentation and brace languages."""
    brace = _brace_depth(text)
    stack: list[int] = []
    deepest = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//"):
            continue
        indent = len(line.expandtabs()) - len(line.lstrip())
        while stack and indent <= stack[-1]:
            stack.pop()
        if re.match(r"(if|for|while|elif)\b", stripped):
            stack.append(indent)
            deepest = max(deepest, len(stack))
    return max(deepest, brace)


def bare_catch_in_text(text: str) -> bool:
    if re.search(r"\bcatch\s*\{", text):
        return True
    if re.search(r"\bcatch\s*\(\s*\)", text):
        return True
    if re.search(r"\bexcept\s*:", text):
        return True
    return False


def swallowing_catch_in_text(text: str) -> bool:
    for match in _CATCH.finditer(text):
        catch_body = _brace_body(text, match.end() - 1)
        if catch_body is None:
            continue
        stripped = catch_body.strip()
        if stripped and stripped not in {";", "pass", "// ignore", "/* ignore */"}:
            continue
        return True
    for match in _PY_EXCEPT.finditer(text):
        tail = text[match.end() :]
        if re.match(r"^\s*pass\b", tail, re.M):
            return True
    return False


def unnamed_literal_numbers_in_text(text: str) -> list[str]:
    code = _STRING.sub('""', text)
    found: list[str] = []
    for raw in _NUMBER.findall(code):
        value = float(raw)
        if value in _SAFE_NUMBERS:
            continue
        found.append(raw)
    return found


def apply_brace_body_metrics(operation: "Operation", body: str) -> None:
    """Fill rule fields from a C-family method body (inside `{` … `}`)."""
    operation.max_control_flow_depth = control_flow_depth_in_text(body)
    operation.has_bare_catch = bare_catch_in_text(body)
    operation.swallows_exceptions = swallowing_catch_in_text(body)
    operation.unnamed_literal_numbers = unnamed_literal_numbers_in_text(body)


def apply_python_function_metrics(operation: "Operation", node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
    """Fill rule fields from a Python function AST node."""
    operation.max_control_flow_depth = _python_control_flow_depth(node)
    bare, swallow = _python_except_flags(node)
    operation.has_bare_catch = bare
    operation.swallows_exceptions = swallow
    operation.unnamed_literal_numbers = _python_unnamed_numbers(node)


def _python_control_flow_depth(node: ast.AST) -> int:
    deepest = 0

    def visit(block: list[ast.stmt], depth: int) -> None:
        nonlocal deepest
        deepest = max(deepest, depth)
        for stmt in block:
            if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With)):
                visit(stmt.body, depth + 1)
                if isinstance(stmt, ast.If) and stmt.orelse:
                    visit(stmt.orelse, depth + 1)
            elif isinstance(stmt, ast.Try):
                visit(stmt.body, depth + 1)
                for handler in stmt.handlers:
                    visit(handler.body, depth + 1)

    visit(getattr(node, "body", []), 0)
    return deepest


def _python_except_flags(node: ast.AST) -> tuple[bool, bool]:
    bare = False
    swallow = False
    for child in ast.walk(node):
        if not isinstance(child, ast.ExceptHandler):
            continue
        if child.type is None:
            bare = True
        body = child.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            swallow = True
        elif not body:
            swallow = True
    return bare, swallow


def _python_unnamed_numbers(node: ast.AST) -> list[str]:
    found: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, (int, float)):
            value = float(child.value)
            if value in _SAFE_NUMBERS:
                continue
            found.append(str(child.value))
    return found
