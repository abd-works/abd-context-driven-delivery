"""Fallback source-span helpers when graph nodes lack a parsed Operation."""

from __future__ import annotations

import re

from practices.clean_engineering.model.operation_metrics import (
    bare_catch_in_text,
    control_flow_depth_in_text,
    swallowing_catch_in_text,
    unnamed_literal_numbers_in_text,
)


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


def control_flow_depth(text: str) -> int:
    return control_flow_depth_in_text(text)


def class_body(text: str, name: str) -> str:
    match = re.search(rf"\bclass\s+{re.escape(name)}\b[^{{]*\{{", text)
    if match is None:
        return ""
    return brace_body(text, match.end() - 1) or ""


def method_body(text: str, method_name: str) -> str:
    match = re.search(rf"\bdef\s+{re.escape(method_name)}\s*\([^)]*\)\s*:", text)
    if match is None:
        match = re.search(rf"\b{re.escape(method_name)}\s*\([^)]*\)\s*\{{", text)
    if match is None:
        return ""
    if "def " in match.group(0):
        lines = text[match.end() :].splitlines()
        body_lines: list[str] = []
        if not lines:
            return ""
        base_indent = len(lines[0].expandtabs()) - len(lines[0].lstrip()) if lines[0].strip() else 0
        for line in lines:
            if not line.strip():
                body_lines.append(line)
                continue
            indent = len(line.expandtabs()) - len(line.lstrip())
            if body_lines and indent <= base_indent and line.strip():
                break
            body_lines.append(line)
        return "\n".join(body_lines)
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
    return unnamed_literal_numbers_in_text(span)


def bare_catch_in_span(span: str) -> bool:
    return bare_catch_in_text(span)


def swallowing_catch_in_span(span: str) -> bool:
    return swallowing_catch_in_text(span)
