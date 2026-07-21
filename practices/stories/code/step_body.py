"""Channel-side step-body analysis — language knowledge lives here, not in scanners.

Each code channel calls these helpers while parsing a tier/test file, then stores
results on TestSuite / TestCase. Scanners only read the model fields.
"""

from __future__ import annotations

import re
from typing import List, Tuple

_TODO_MARKERS = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b")

_TS_STEP = re.compile(
    r"['\"`](?P<key>[^'\"`\n]+)['\"`]\s*:\s*(?:async\s*)?\(\s*\)\s*=>\s*\{"
    r"(?P<body>[^{}]*?)\}",
    re.DOTALL,
)

_PY_STEP_DEF = re.compile(
    r"^\s*def\s+(?P<name>(?:given|when|then)_\w+)\s*\(self[^)]*\)\s*(?:->\s*None\s*)?:\s*"
    r"(?P<body>(?:\n\s+.+)+?)(?=\n\s*def\s|\Z)",
    re.MULTILINE,
)

_PY_STEP_DEF_PRIVATE = re.compile(
    r"^\s*def\s+(?P<name>_(?:given|when|then)_\w+)\s*\(self[^)]*\)\s*(?:->\s*None\s*)?:\s*"
    r"(?P<body>(?:\n\s+.+)+?)(?=\n\s*def\s|\Z)",
    re.MULTILINE,
)

_JAVA_STEP_LAMBDA = re.compile(
    r"put\s*\(\s*\"(?P<key>[^\"]+)\"\s*,\s*\(\)\s*->\s*\{(?P<body>[^{}]*?)\}\s*\)",
    re.DOTALL,
)


def body_is_stub(body: str) -> bool:
    stripped_lines: List[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("//") or line.startswith("#"):
            continue
        if line.startswith("/*") or line.startswith("*") or line.startswith("*/"):
            continue
        if re.match(r'^(?:"""|\'\'\')', line):
            continue
        stripped_lines.append(line)

    if not stripped_lines:
        return True

    joined = "\n".join(stripped_lines)
    if _TODO_MARKERS.search(joined):
        return True
    if re.search(r"raise\s+NotImplementedError\b", joined):
        return True
    if re.search(r"throw\s+new\s+Error\s*\(\s*['\"`]not implemented", joined, re.IGNORECASE):
        return True
    if joined in ("pass", "pass;", "{}", "return;", "return null;", "return;"):
        return True
    return False


def unimplemented_steps_typescript(text: str) -> List[str]:
    return [
        m.group("key")
        for m in _TS_STEP.finditer(text)
        if body_is_stub(m.group("body") or "")
    ]


def unimplemented_steps_javascript(text: str) -> List[str]:
    return unimplemented_steps_typescript(text)


def unimplemented_steps_python(text: str) -> List[str]:
    found: List[str] = []
    for pattern in (_PY_STEP_DEF, _PY_STEP_DEF_PRIVATE):
        for m in pattern.finditer(text):
            body = m.group("body") or ""
            body_no_doc = "\n".join(
                line for line in body.splitlines()
                if not re.match(r'^\s*(?:"""|\'\'\')', line)
            )
            if body_is_stub(body_no_doc):
                found.append(m.group("name"))
    return found


def unimplemented_steps_java(text: str) -> List[str]:
    return [
        m.group("key")
        for m in _JAVA_STEP_LAMBDA.finditer(text)
        if body_is_stub(m.group("body") or "")
    ]


def case_body_is_stub(body: str) -> bool:
    """True when a test method body is still a scaffold stub."""
    return body_is_stub(body)
