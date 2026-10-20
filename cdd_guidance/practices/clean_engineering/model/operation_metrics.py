"""Rule-oriented facts extracted from operation bodies — shared by parsers."""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.operation import Operation

_CATCH = re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{")
_PY_EXCEPT = re.compile(r"\bexcept\s*(?::|\([^)]*\)\s*:)")
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_NUMBER = re.compile(r"\b(\d+(?:\.\d+)?)\b")
_REGEXP_LITERAL = re.compile(r"/(?:\\.|[^/\\])*/[gimsuy]*")
_SAFE_NUMBERS = {
    0,
    1,
    2,
    3,
    4,
    5,
    -1,
    0.0,
    1.0,
    0.5,
    8,
    9,
    10,
    100,
    200,
    201,
    204,
    301,
    302,
    400,
    401,
    403,
    404,
    409,
    422,
    500,
    502,
    503,
}
_NARRATIVE_COMMENT = re.compile(
    r"(?:transient|value object|carries|implementation|see also|cross-ref)",
    re.IGNORECASE,
)


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
    # TypeScript optional catch binding `catch {` is intentional — not a bare handler.
    if re.search(r"\bcatch\s*\{", text):
        return False
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
    code = _REGEXP_LITERAL.sub('""', code)
    found: list[str] = []
    for raw in _NUMBER.findall(code):
        value = float(raw)
        if value in _SAFE_NUMBERS:
            continue
        found.append(raw)
    return found


_OWN_RECEIVERS = frozenset({"this", "self", "super"})
_WIRED_PEER_FIELDS = frozenset({"repository", "repo"})


def _parameter_names(operation: "Operation") -> frozenset[str]:
    return frozenset(param.name for param in operation.parameters if param.name)


def _same_type_field_copy(body: str, receiver: str, field: str) -> bool:
    """``this._field = receiver._field`` (or public ``field``) — aggregate copies from a peer instance."""
    return bool(
        re.search(
            rf"(?:this|self)\._?{re.escape(field)}\s*=\s*{re.escape(receiver)}\._?{re.escape(field)}\b",
            body,
        )
    )


def peer_private_access_in_text(body: str, parameter_names: frozenset[str] | None = None) -> bool:
    """True when the body reads another object's ``._`` field (not ``this._`` / ``self._``)."""
    params = parameter_names or frozenset()
    for match in re.finditer(r"(\w+)\._(\w+)", body):
        receiver, field = match.group(1), match.group(2)
        if receiver in _OWN_RECEIVERS:
            continue
        if field in _WIRED_PEER_FIELDS:
            continue
        if receiver in params and _same_type_field_copy(body, receiver, field):
            continue
        return True
    return False


def apply_brace_body_metrics(operation: "Operation", body: str) -> None:
    """Fill rule fields from a C-family method body (inside `{` … `}`)."""
    operation.max_control_flow_depth = control_flow_depth_in_text(body)
    operation.has_bare_catch = bare_catch_in_text(body)
    operation.swallows_exceptions = swallowing_catch_in_text(body)
    operation.unnamed_literal_numbers = unnamed_literal_numbers_in_text(body)
    operation.peer_private_access = peer_private_access_in_text(body, _parameter_names(operation))


def apply_python_function_metrics(operation: "Operation", node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
    """Fill rule fields from a Python function AST node."""
    operation.max_control_flow_depth = _python_control_flow_depth(node)
    bare, swallow = _python_except_flags(node)
    operation.has_bare_catch = bare
    operation.swallows_exceptions = swallow
    operation.unnamed_literal_numbers = _python_unnamed_numbers(node)
    operation.narrative_comment_lines = 0
    operation.peer_private_access = _python_peer_private_access(node)


def _python_peer_private_access(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    params = {a.arg for a in node.args.args if a.arg != "self"}
    params.update(a.arg for a in node.args.kwonlyargs)
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
            if child.value.id not in params or not child.attr.startswith("_"):
                continue
            if child.attr.lstrip("_") in _WIRED_PEER_FIELDS or child.attr in _WIRED_PEER_FIELDS:
                continue
            if _python_same_type_field_copy(node, child.value.id, child.attr):
                continue
            return True
    return False


def _python_same_type_field_copy(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    param_name: str,
    attr: str,
) -> bool:
    field = attr.lstrip("_")
    for child in ast.walk(node):
        if not isinstance(child, ast.Assign) or len(child.targets) != 1:
            continue
        target = child.targets[0]
        value = child.value
        if not isinstance(target, ast.Attribute) or not isinstance(value, ast.Attribute):
            continue
        if not isinstance(target.value, ast.Name) or target.value.id != "self":
            continue
        if not isinstance(value.value, ast.Name) or value.value.id != param_name:
            continue
        if target.attr.lstrip("_") == field and value.attr.lstrip("_") == field:
            return True
    return False


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
