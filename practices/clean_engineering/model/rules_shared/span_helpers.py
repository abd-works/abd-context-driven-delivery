"""Source-span helpers when the class model does not carry enough detail."""

from __future__ import annotations

import re

_CATCH = re.compile(r"\bcatch\s*(\([^)]*\))?\s*\{")
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
_NUMBER = re.compile(r"\b(\d+(?:\.\d+)?)\b")
_SAFE_NUMBERS = {0, 1, 2, -1, 0.0, 1.0, 0.5, 10, 100}


def brace_body(text: str, open_index: int) -> str | None:
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


def brace_depth(text: str) -> int:
    depth = 0
    deepest = 0
    for character in text:
        if character == "{":
            depth += 1
            deepest = max(deepest, depth)
        elif character == "}":
            depth = max(0, depth - 1)
    return deepest


def class_body(text: str, name: str) -> str:
    match = re.search(rf"\bclass\s+{re.escape(name)}\b[^{{]*\{{", text)
    if match is None:
        return ""
    return brace_body(text, match.end() - 1) or ""


def constructor_body(class_body_text: str) -> str:
    match = re.search(r"\bconstructor\s*\([^)]*\)\s*\{", class_body_text)
    if match is None:
        match = re.search(r"\bdef\s+__init__\s*\([^)]*\)\s*:", class_body_text)
    if match is None:
        return ""
    if "def __init__" in match.group(0):
        return ""
    return brace_body(class_body_text, match.end() - 1) or ""


def unnamed_numbers_in_span(span: str) -> list[str]:
    code = _STRING.sub('""', span)
    found: list[str] = []
    for raw in _NUMBER.findall(code):
        value = float(raw)
        if value in _SAFE_NUMBERS:
            continue
        found.append(raw)
    return found


def bare_catch_in_span(span: str) -> bool:
    for match in _CATCH.finditer(span):
        binding = (match.group(1) or "").strip()
        if binding and binding != "()":
            continue
        return True
    return False


def swallowing_catch_in_span(span: str) -> bool:
    for match in _CATCH.finditer(span):
        catch_body = brace_body(span, match.end() - 1)
        if catch_body is None:
            continue
        stripped = catch_body.strip()
        if stripped and stripped not in {";", "pass", "// ignore", "/* ignore */"}:
            continue
        return True
    return False
