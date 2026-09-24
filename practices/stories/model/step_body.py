"""Channel-side step-body analysis - language knowledge lives here, not in scanners.

Each code channel calls these helpers while parsing a tier/test file, then stores
results on TestSuite / TestCase. Scanners only read the model fields.
"""

from __future__ import annotations

import re
from typing import List

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


class StepBody:
    def _code_lines(self, body: str) -> List[str]:
        stripped_lines: List[str] = []
        for raw in body.splitlines():
            line = raw.strip()
            if not line or self._is_comment(line):
                continue
            stripped_lines.append(line)
        return stripped_lines

    def _is_comment(self, line: str) -> bool:
        if line.startswith("//") or line.startswith("#"):
            return True
        if line.startswith("/*") or line.startswith("*") or line.startswith("*/"):
            return True
        return bool(re.match(r'^(?:"""|\'\'\')', line))

    def _is_empty_stub(self, joined: str) -> bool:
        if _TODO_MARKERS.search(joined):
            return True
        if re.search(r"raise\s+NotImplementedError\b", joined):
            return True
        if re.search(r"throw\s+new\s+Error\s*\(\s*['\"`]not implemented", joined, re.IGNORECASE):
            return True
        return joined in ("pass", "pass;", "{}", "return;", "return null;", "return;")

    def is_stub(self, body: str) -> bool:
        stripped_lines = self._code_lines(body)
        if not stripped_lines:
            return True
        return self._is_empty_stub("\n".join(stripped_lines))

    def case_is_stub(self, body: str) -> bool:
        return self.is_stub(body)

    def unimplemented_typescript(self, text: str) -> List[str]:
        return [
            m.group("key")
            for m in _TS_STEP.finditer(text)
            if self.is_stub(m.group("body") or "")
        ]

    def unimplemented_javascript(self, text: str) -> List[str]:
        return self.unimplemented_typescript(text)

    def unimplemented_python(self, text: str) -> List[str]:
        found: List[str] = []
        for pattern in (_PY_STEP_DEF, _PY_STEP_DEF_PRIVATE):
            for m in pattern.finditer(text):
                body_no_doc = "\n".join(
                    line for line in (m.group("body") or "").splitlines()
                    if not re.match(r'^\s*(?:"""|\'\'\')', line)
                )
                if self.is_stub(body_no_doc):
                    found.append(m.group("name"))
        return found

    def unimplemented_java(self, text: str) -> List[str]:
        return [
            m.group("key")
            for m in _JAVA_STEP_LAMBDA.finditer(text)
            if self.is_stub(m.group("body") or "")
        ]
