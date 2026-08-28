"""Scanner: flaccid-data-object-no-behavior — domain types must own operations."""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner, ScannerRunner

RULE = "flaccid-data-object-no-behavior"
_TS_SUFFIXES = frozenset({".ts", ".tsx"})
_TYPE_DECL = re.compile(
    r"\b(?:export\s+)?(?:interface|class|type)\s+([A-Za-z_][A-Za-z0-9_]*)"
)
_EXEMPT_SUFFIXES = (
    "Props",
    "DTO",
    "Config",
    "Options",
    "Attributes",
    "Params",
    "Partial",
)
_METHOD = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|async|static)\s+)*"
    r"[A-Za-z_][A-Za-z0-9_]*\s*(?:<[^>]+>)?\s*\("
)
_PROPERTY = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|static)\s+)*"
    r"[A-Za-z_][A-Za-z0-9_]*\??\s*:"
)


def _block_after(content: str, start: int) -> str:
    brace = content.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index, char in enumerate(content[brace:], brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[brace + 1 : index]
    return content[brace + 1 :]


def _is_exempt(name: str) -> bool:
    return any(name.endswith(suffix) for suffix in _EXEMPT_SUFFIXES)


class FlaccidDataObjectNoBehaviorScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in _TS_SUFFIXES:
            return []
        content = file_path.read_text(encoding="utf-8", errors="replace")
        if not content:
            return []
        violations = []
        for match in _TYPE_DECL.finditer(content):
            name = match.group(1)
            if _is_exempt(name):
                continue
            body = _block_after(content, match.end())
            if not body.strip():
                continue
            has_method = False
            has_property = False
            for raw_line in body.splitlines():
                line = raw_line.split("//")[0].rstrip()
                if not line.strip():
                    continue
                if _METHOD.search(line):
                    has_method = True
                    continue
                if _PROPERTY.search(line):
                    has_property = True
            if has_property and not has_method:
                line = content[: match.start()].count("\n") + 1
                violations.append(
                    self.violation(
                        f"'{name}' is a flaccid data object (properties only). "
                        "Give the domain type the operations that belong to it.",
                        location=str(file_path),
                        line=line,
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            FlaccidDataObjectNoBehaviorScanner,
            RULE,
            lambda root: sorted(root.rglob("*.ts")),
        )
    )
