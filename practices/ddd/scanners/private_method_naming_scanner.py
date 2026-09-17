"""Scanner: private-method-naming — UML '-' with '_' vs public '+' without."""
from __future__ import annotations

import html
import re
from pathlib import Path

from scan import Scanner, ScannerRunner

RULE = "private-method-naming"
_OP = re.compile(r"([+\-#])\s*(_?[A-Za-z][A-Za-z0-9]*)\s*\(")
_DERIVE = re.compile(r"^derive[A-Z]")
_SUFFIXES = frozenset({".drawio", ".xml", ".md", ".puml", ".txt"})


def _visible_text(file_path: Path, content: str) -> str:
    if file_path.suffix.lower() in {".drawio", ".xml"}:
        return html.unescape(content)
    return content


class PrivateMethodNamingScanner(Scanner):
    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix.lower() not in _SUFFIXES:
            return []
        raw = file_path.read_text(encoding="utf-8", errors="replace")
        if not raw:
            return []
        text = _visible_text(file_path, raw)
        violations = []
        for index, line in enumerate(text.splitlines(), 1):
            for match in _OP.finditer(line):
                visibility, name = match.group(1), match.group(2)
                if visibility == "+" and name.startswith("_"):
                    violations.append(
                        self.violation(
                            f"Public operation '{name}' must not use a '_' prefix.",
                            location=str(file_path),
                            line=index,
                        )
                    )
                elif visibility == "-" and not name.startswith("_"):
                    violations.append(
                        self.violation(
                            f"Private operation '{name}' must use a '_' prefix "
                            f"(e.g. _{name}).",
                            location=str(file_path),
                            line=index,
                        )
                    )
                elif visibility == "+" and _DERIVE.match(name):
                    violations.append(
                        self.violation(
                            f"Internal helper '{name}' must use '-' visibility "
                            f"and a '_' prefix (e.g. - _{name}).",
                            location=str(file_path),
                            line=index,
                        )
                    )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            PrivateMethodNamingScanner,
            RULE,
            lambda root: sorted(root.rglob("*")),
        )
    )
