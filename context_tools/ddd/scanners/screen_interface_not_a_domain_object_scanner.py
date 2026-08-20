"""Scanner: screen-interface-not-a-domain-object — UI drivers are not domain types."""
from __future__ import annotations

import re
from pathlib import Path

from scanners import Scanner, ScannerRunner

RULE = "screen-interface-not-a-domain-object"
_TS_SUFFIXES = frozenset({".ts", ".tsx", ".js", ".jsx"})
_TYPE_DECL = re.compile(
    r"\b(?:export\s+)?(?:interface|class|type)\s+([A-Za-z_][A-Za-z0-9_]*)"
)
_OPEN = re.compile(r"\bopen\s*\(")
_SHOWN = re.compile(r"\bis\w*(?:Showing|Shown)\w*\s*\(")


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


class ScreenInterfaceNotADomainObjectScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in _TS_SUFFIXES:
            return []
        content = file_path.read_text(encoding="utf-8", errors="replace")
        if not content:
            return []
        violations = []
        for match in _TYPE_DECL.finditer(content):
            body = _block_after(content, match.end())
            if _OPEN.search(body) and _SHOWN.search(body):
                line = content[: match.start()].count("\n") + 1
                name = match.group(1)
                violations.append(
                    self.violation(
                        f"'{name}' looks like a screen driver (open / isShowing), "
                        "not a domain object. Put the operation on the aggregate.",
                        location=str(file_path),
                        line=line,
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            ScreenInterfaceNotADomainObjectScanner,
            RULE,
            lambda root: sorted(root.rglob("*.ts")),
        )
    )
