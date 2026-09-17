"""Shared helpers for BDD scanners — file shaping and it-body extraction."""
from __future__ import annotations

import re
from pathlib import Path

_SPEC_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".java")
_JS_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs")
_SKETCH_NAMES = ("hierarchy.txt",)

_IT_OPEN_PY = re.compile(
    r"""^\s*with\s+it\s*\(\s*['"](.+?)['"]\s*\)\s*:\s*$"""
)
_IT_OPEN_JS = re.compile(
    r"""(?:^|\s)it\s*\(\s*['"`](.+?)['"`]\s*,\s*(?:async\s*)?\(?\s*\)?\s*=>\s*\{"""
)
_IT_OPEN_JAVA = re.compile(
    r"""@Test\s*\n\s*(?:public\s+)?void\s+(should\w*)\s*\(""",
    re.MULTILINE,
)

_SIGNATURE_MARKERS = ("# BDD: SIGNATURE", "// BDD: SIGNATURE")


def is_spec_file(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() not in _SPEC_SUFFIXES:
        return False
    return (
        name.endswith("_spec.py")
        or "_spec." in name
        or ".test." in name
        or ".spec." in name
        or name.endswith("test.java")
        or name.endswith("tests.java")
    )


def is_sketch_file(path: Path) -> bool:
    name = path.name.lower()
    if name in _SKETCH_NAMES:
        return True
    return (
        name.endswith("-hierarchy.txt")
        or name.endswith("_hierarchy.txt")
        or ("sketch" in name and path.suffix.lower() in {".md", ".txt"})
    )


def is_js_spec(path: Path) -> bool:
    return path.suffix.lower() in _JS_SUFFIXES and is_spec_file(path)


def is_python_spec(path: Path) -> bool:
    return path.suffix.lower() == ".py" and is_spec_file(path)


def is_java_spec(path: Path) -> bool:
    return path.suffix.lower() == ".java" and is_spec_file(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def has_signature_marker(content: str) -> bool:
    return any(marker in content for marker in _SIGNATURE_MARKERS)


def extract_it_blocks(path: Path, content: str) -> list[tuple[int, str, str]]:
    """Return ``(line_number, label, body)`` for each behavior block."""
    if is_python_spec(path):
        return _extract_python_it_blocks(content)
    if is_js_spec(path):
        return _extract_js_it_blocks(content)
    if is_java_spec(path):
        return _extract_java_it_blocks(content)
    return []


def _extract_python_it_blocks(content: str) -> list[tuple[int, str, str]]:
    lines = content.splitlines()
    results: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        match = _IT_OPEN_PY.match(line)
        if not match:
            continue
        label = match.group(1)
        base_indent = len(line) - len(line.lstrip())
        body_lines: list[str] = []
        for j in range(i + 1, len(lines)):
            nxt = lines[j]
            if not nxt.strip():
                body_lines.append(nxt)
                continue
            indent = len(nxt) - len(nxt.lstrip())
            if indent <= base_indent:
                break
            body_lines.append(nxt)
        results.append((i + 1, label, "\n".join(body_lines)))
    return results


def _extract_js_it_blocks(content: str) -> list[tuple[int, str, str]]:
    lines = content.splitlines()
    results: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        match = _IT_OPEN_JS.search(line)
        if not match:
            continue
        label = match.group(1)
        depth = 0
        body_lines: list[str] = []
        in_body = False
        for j in range(i, min(i + 80, len(lines))):
            current = lines[j]
            for ch in current:
                if ch == "{":
                    depth += 1
                    if depth == 1:
                        in_body = True
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
            if in_body and depth > 0 and j > i:
                body_lines.append(current)
            if depth == 0 and in_body:
                break
        results.append((i + 1, label, "\n".join(body_lines)))
    return results


def _extract_java_it_blocks(content: str) -> list[tuple[int, str, str]]:
    results: list[tuple[int, str, str]] = []
    for match in _IT_OPEN_JAVA.finditer(content):
        label = match.group(1)
        start = content.count("\n", 0, match.start()) + 1
        # Body is everything until the next unmatched closing brace after the method open.
        after = content[match.end() :]
        brace = after.find("{")
        if brace < 0:
            results.append((start, label, ""))
            continue
        depth = 0
        end = brace
        for idx, ch in enumerate(after[brace:], start=brace):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = idx
                    break
        body = after[brace + 1 : end]
        results.append((start, label, body))
    return results
